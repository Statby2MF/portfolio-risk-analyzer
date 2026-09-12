"""
Optimisation de portefeuille : Markowitz, frontière efficiente
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def portfolio_return(returns_df, weights):
    """Rendement annualisé du portefeuille"""
    return np.sum(returns_df.mean() * weights) * 252


def portfolio_volatility(returns_df, weights):
    """Volatilité annualisée du portefeuille"""
    cov = returns_df.cov() * 252
    return np.sqrt(weights.T @ cov @ weights)


def portfolio_sharpe(returns_df, weights, rf=0.02):
    """Ratio de Sharpe du portefeuille"""
    ret = portfolio_return(returns_df, weights)
    vol = portfolio_volatility(returns_df, weights)
    if vol == 0:
        return 0
    return (ret - rf) / vol


def optimize_max_sharpe(returns_df):
    """Trouve les poids qui maximisent le ratio de Sharpe"""
    n = len(returns_df.columns)
    
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n))
    init = np.array([1/n] * n)
    
    result = minimize(
        lambda w: -portfolio_sharpe(returns_df, w),
        init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000}
    )
    
    if result.success:
        return result.x
    return init


def optimize_min_volatility(returns_df):
    """Trouve les poids qui minimisent la volatilité"""
    n = len(returns_df.columns)
    
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n))
    init = np.array([1/n] * n)
    
    result = minimize(
        lambda w: portfolio_volatility(returns_df, w),
        init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000}
    )
    
    if result.success:
        return result.x
    return init


def optimize_risk_parity(returns_df):
    """Risk Parity : chaque actif contribue equally au risque"""
    n = len(returns_df.columns)
    cov = returns_df.cov() * 252
    
    def risk_parity_objective(w):
        portfolio_var = w.T @ cov @ w
        marginal_contrib = cov @ w
        risk_contrib = w * marginal_contrib / np.sqrt(portfolio_var)
        target = np.sqrt(portfolio_var) / n
        return np.sum((risk_contrib - target) ** 2)
    
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = tuple((0.01, 1) for _ in range(n))
    init = np.array([1/n] * n)
    
    result = minimize(
        risk_parity_objective,
        init,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000}
    )
    
    if result.success:
        return result.x
    return init


def get_optimal_portfolios(returns_df):
    """Retourne les 3 portefeuilles optimaux"""
    return {
        "max_sharpe": optimize_max_sharpe(returns_df),
        "min_volatility": optimize_min_volatility(returns_df),
        "risk_parity": optimize_risk_parity(returns_df),
    }
