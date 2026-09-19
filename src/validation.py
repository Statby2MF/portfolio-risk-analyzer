"""
Validation in-sample / out-of-sample et walk-forward
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Ajouter le dossier parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_optimizer import (
    optimize_max_sharpe,
    optimize_min_volatility,
    optimize_risk_parity,
    portfolio_return,
    portfolio_volatility,
    portfolio_sharpe
)
from risk_metrics import calculate_all_metrics


def split_in_out(returns_df, train_ratio=0.7):
    """
    Sépare les données en in-sample (train) et out-of-sample (test)
    """
    n = len(returns_df)
    split_idx = int(n * train_ratio)
    
    train = returns_df.iloc[:split_idx]
    test = returns_df.iloc[split_idx:]
    
    return train, test


def evaluate_portfolio(returns_df, weights):
    """
    Évalue un portefeuille sur une période
    """
    portfolio_returns = returns_df.dot(weights)
    portfolio_prices = (1 + portfolio_returns).cumprod() * 100
    
    metrics = calculate_all_metrics(portfolio_returns, portfolio_prices)
    
    return {
        "return": portfolio_return(returns_df, weights),
        "volatility": portfolio_volatility(returns_df, weights),
        "sharpe": portfolio_sharpe(returns_df, weights),
        "max_drawdown": metrics['max_drawdown'],
        "var_95": metrics['var_95_historique'],
        "var_99": metrics['var_99_historique'],
        "es_99": metrics['es_99'],
        "returns_series": portfolio_returns,
    }


def in_out_validation(returns_df, train_ratio=0.7):
    """
    Validation in-sample / out-of-sample
    """
    train, test = split_in_out(returns_df, train_ratio)
    
    # Optimiser sur in-sample
    portfolios = {
        "Max Sharpe": optimize_max_sharpe(train),
        "Min Volatilité": optimize_min_volatility(train),
        "Risk Parity": optimize_risk_parity(train),
    }
    
    results = {}
    for name, weights in portfolios.items():
        # Performance in-sample
        perf_in = evaluate_portfolio(train, weights)
        
        # Performance out-of-sample (mêmes poids !)
        perf_out = evaluate_portfolio(test, weights)
        
        results[name] = {
            "in_sample": perf_in,
            "out_of_sample": perf_out,
            "weights": weights,
            "sharpe_decay": perf_in['sharpe'] - perf_out['sharpe'],
            "sharpe_ratio_out_in": perf_out['sharpe'] / perf_in['sharpe'] if perf_in['sharpe'] != 0 else 0,
        }
    
    return results, train, test


def walk_forward_validation(returns_df, n_windows=5, train_ratio=0.7):
    """
    Walk-forward validation : fenêtres glissantes
    """
    n = len(returns_df)
    window_size = n // n_windows
    
    results = []
    
    for i in range(n_windows):
        start = i * window_size
        end = start + window_size
        
        if end > n:
            break
        
        window_data = returns_df.iloc[start:end]
        
        if len(window_data) < 50:
            continue
        
        # Split
        train, test = split_in_out(window_data, train_ratio)
        
        if len(train) < 30 or len(test) < 10:
            continue
        
        # Optimiser
        try:
            weights = optimize_max_sharpe(train)
            perf_out = evaluate_portfolio(test, weights)
            
            results.append({
                "window": i + 1,
                "start": window_data.index[0],
                "end": window_data.index[-1],
                "sharpe_out": perf_out['sharpe'],
                "return_out": perf_out['return'],
                "volatility_out": perf_out['volatility'],
                "max_dd_out": perf_out['max_drawdown'],
            })
        except:
            continue
    
    return pd.DataFrame(results)


def print_validation_report(results):
    """
    Affiche un rapport de validation
    """
    print("=" * 80)
    print("📊 VALIDATION IN-SAMPLE / OUT-OF-SAMPLE")
    print("=" * 80)
    print()
    
    for name, res in results.items():
        print(f"🎯 {name}")
        print("-" * 80)
        
        in_s = res['in_sample']
        out_s = res['out_of_sample']
        
        print(f"{'Métrique':<25} {'In-Sample':>15} {'Out-of-Sample':>15} {'Dégradation':>15}")
        print("-" * 80)
        
        metrics = [
            ("Rendement annualisé", 'return', True),
            ("Volatilité", 'volatility', True),
            ("Ratio de Sharpe", 'sharpe', False),
            ("Max Drawdown", 'max_drawdown', True),
            ("VaR 95%", 'var_95', True),
            ("VaR 99%", 'var_99', True),
            ("ES 99%", 'es_99', True),
        ]
        
        for label, key, is_pct in metrics:
            in_val = in_s[key]
            out_val = out_s[key]
            
            if is_pct:
                in_str = f"{in_val*100:.2f}%"
                out_str = f"{out_val*100:.2f}%"
            else:
                in_str = f"{in_val:.3f}"
                out_str = f"{out_val:.3f}"
            
            # Dégradation en %
            if abs(in_val) > 0.001:
                degrad = ((out_val - in_val) / abs(in_val)) * 100
                degrad_str = f"{degrad:+.1f}%"
            else:
                degrad_str = "N/A"
            
            print(f"{label:<25} {in_str:>15} {out_str:>15} {degrad_str:>15}")
        
        print()
        print(f"⚠️ Sharpe decay : {res['sharpe_decay']:.3f}")
        print(f"📉 Ratio out/in : {res['sharpe_ratio_out_in']:.2f}")
        
        if res['sharpe_ratio_out_in'] > 0.7:
            print("✅ Validation favorable (à confirmer sur d'autres fenêtres)")
        elif res['sharpe_ratio_out_in'] > 0.4:
            print("⚠️ Le modèle est MOYENNEMENT robuste")
        else:
            print("❌ Le modèle a probablement SUR-APPRIS")
        
        print()


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.data_manager import load_portfolio
    
    # Charger quelques actions
    assets = ["BRVM_SNTS", "BRVM_ORAC", "BRVM_SGBC", "BRVM_ECOC"]
    prices = load_portfolio(assets)
    
    if prices is not None:
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Validation
        results, train, test = in_out_validation(returns, train_ratio=0.7)
        print_validation_report(results)
        
        # Walk-forward
        print("\n" + "=" * 80)
        print("📊 WALK-FORWARD VALIDATION")
        print("=" * 80)
        wf = walk_forward_validation(returns, n_windows=5)
        print(wf.to_string(index=False))
