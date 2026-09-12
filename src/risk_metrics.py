"""
Métriques de risque pour portefeuille.
VaR, Expected Shortfall, volatilité, drawdown, ratios.
"""
import numpy as np
import pandas as pd
from scipy import stats


def calculate_returns(prices):
    """Calcule les rendements logarithmiques"""
    if isinstance(prices, pd.Series):
        returns = np.log(prices / prices.shift(1)).dropna()
    else:
        returns = np.diff(np.log(prices))
        returns = returns[~np.isnan(returns)]
    return returns


def calculate_volatility(returns, annualize=True):
    """Calcule la volatilité annualisée"""
    vol = np.std(returns)
    if annualize:
        vol = vol * np.sqrt(252)
    return vol


def calculate_var_historical(returns, confidence=0.95):
    """VaR historique (percentile des pertes)"""
    return np.percentile(returns, (1 - confidence) * 100)


def calculate_var_parametric(returns, confidence=0.95):
    """VaR paramétrique (loi normale)"""
    mu = np.mean(returns)
    sigma = np.std(returns)
    z = stats.norm.ppf(1 - confidence)
    return mu + z * sigma


def calculate_var_cornish_fisher(returns, confidence=0.95):
    """VaR avec expansion de Cornish-Fisher (tient compte skewness et kurtosis)"""
    mu = np.mean(returns)
    sigma = np.std(returns)
    z = stats.norm.ppf(1 - confidence)
    
    s = stats.skew(returns)
    k = stats.kurtosis(returns)
    
    z_cf = (z + (z**2 - 1) * s / 6 + (z**3 - 3*z) * (k - 3) / 24 
            - (2*z**3 - 5*z) * s**2 / 36)
    
    return mu + z_cf * sigma


def calculate_expected_shortfall(returns, confidence=0.95):
    """Expected Shortfall (perte moyenne au-delà de la VaR)"""
    var = calculate_var_historical(returns, confidence)
    es = returns[returns <= var].mean()
    return es


def calculate_max_drawdown(prices):
    """Drawdown maximal"""
    if isinstance(prices, pd.Series):
        prices = prices.values
    
    cumulative = np.cumprod(1 + calculate_returns(prices))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    return np.min(drawdown)


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Ratio de Sharpe"""
    excess = returns - risk_free_rate / 252
    if np.std(excess) == 0:
        return 0
    return np.mean(excess) / np.std(excess) * np.sqrt(252)


def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """Ratio de Sortino (ne pénalise que la volatilité à la baisse)"""
    excess = returns - risk_free_rate / 252
    downside = excess[excess < 0]
    if len(downside) == 0 or np.std(downside) == 0:
        return 0
    return np.mean(excess) / np.std(downside) * np.sqrt(252)


def calculate_calmar_ratio(returns, prices):
    """Ratio de Calmar (rendement / drawdown)"""
    annual_return = np.mean(returns) * 252
    max_dd = abs(calculate_max_drawdown(prices))
    if max_dd == 0:
        return 0
    return annual_return / max_dd


def calculate_all_metrics(returns, prices):
    """Calcule toutes les métriques de risque"""
    return {
        "rendement_annualise": np.mean(returns) * 252,
        "volatilite_annuelle": calculate_volatility(returns),
        "var_95_historique": calculate_var_historical(returns, 0.95),
        "var_99_historique": calculate_var_historical(returns, 0.99),
        "var_95_parametrique": calculate_var_parametric(returns, 0.95),
        "var_99_parametrique": calculate_var_parametric(returns, 0.99),
        "var_95_cornish_fisher": calculate_var_cornish_fisher(returns, 0.95),
        "var_99_cornish_fisher": calculate_var_cornish_fisher(returns, 0.99),
        "es_95": calculate_expected_shortfall(returns, 0.95),
        "es_99": calculate_expected_shortfall(returns, 0.99),
        "max_drawdown": calculate_max_drawdown(prices),
        "sharpe": calculate_sharpe_ratio(returns),
        "sortino": calculate_sortino_ratio(returns),
        "skewness": stats.skew(returns),
        "kurtosis": stats.kurtosis(returns),
    }
