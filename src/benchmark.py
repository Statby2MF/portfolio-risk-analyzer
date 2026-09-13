"""
Analyse comparative avec un benchmark
Alpha, Beta, Information Ratio, Tracking Error
"""
import numpy as np
import pandas as pd
from scipy import stats


def calculate_alpha_beta(portfolio_returns, benchmark_returns, risk_free_rate=0.02):
    """
    Calcule l'Alpha et le Beta du portefeuille par rapport au benchmark
    
    Alpha = rendement excédentaire non expliqué par le marché
    Beta = sensibilité du portefeuille aux mouvements du marché
    """
    # Aligner les séries
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port = portfolio_returns.loc[common_idx]
    bench = benchmark_returns.loc[common_idx]
    
    if len(port) < 10:
        return None
    
    # Beta = Cov(port, bench) / Var(bench)
    covariance = np.cov(port, bench)[0, 1]
    variance_bench = np.var(bench, ddof=1)
    beta = covariance / variance_bench if variance_bench != 0 else 0
    
    # Alpha = E[port] - rf - Beta * (E[bench] - rf)
    rf_daily = risk_free_rate / 252
    alpha_daily = np.mean(port) - rf_daily - beta * (np.mean(bench) - rf_daily)
    alpha_annualized = alpha_daily * 252
    
    return {
        "alpha": alpha_annualized,
        "beta": beta,
    }


def calculate_tracking_error(portfolio_returns, benchmark_returns):
    """
    Tracking Error = volatilité de la différence portefeuille - benchmark
    """
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port = portfolio_returns.loc[common_idx]
    bench = benchmark_returns.loc[common_idx]
    
    diff = port - bench
    te = np.std(diff) * np.sqrt(252)
    return te


def calculate_information_ratio(portfolio_returns, benchmark_returns):
    """
    Information Ratio = rendement excédentaire / tracking error
    """
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port = portfolio_returns.loc[common_idx]
    bench = benchmark_returns.loc[common_idx]
    
    excess = port - bench
    if np.std(excess) == 0:
        return 0
    
    ir = (np.mean(excess) * 252) / (np.std(excess) * np.sqrt(252))
    return ir


def calculate_capture_ratios(portfolio_returns, benchmark_returns):
    """
    Up/Down Capture Ratio
    - Up Capture : performance du portefeuille quand le marché monte
    - Down Capture : performance du portefeuille quand le marché baisse
    """
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port = portfolio_returns.loc[common_idx]
    bench = benchmark_returns.loc[common_idx]
    
    # Jours où le benchmark monte
    up_days = bench > 0
    down_days = bench < 0
    
    up_capture = 0
    down_capture = 0
    
    if up_days.sum() > 0:
        up_capture = (port[up_days].mean() / bench[up_days].mean()) * 100
    
    if down_days.sum() > 0:
        down_capture = (port[down_days].mean() / bench[down_days].mean()) * 100
    
    return {
        "up_capture": up_capture,
        "down_capture": down_capture,
    }


def calculate_all_benchmark_metrics(portfolio_returns, benchmark_returns, risk_free_rate=0.02):
    """
    Calcule toutes les métriques de comparaison avec le benchmark
    """
    # Aligner
    common_idx = portfolio_returns.index.intersection(benchmark_returns.index)
    port = portfolio_returns.loc[common_idx]
    bench = benchmark_returns.loc[common_idx]
    
    if len(port) < 10:
        return None
    
    # Métriques
    ab = calculate_alpha_beta(port, bench, risk_free_rate)
    te = calculate_tracking_error(port, bench)
    ir = calculate_information_ratio(port, bench)
    capture = calculate_capture_ratios(port, bench)
    
    # Performance annualisée
    port_return_ann = np.mean(port) * 252
    bench_return_ann = np.mean(bench) * 252
    
    port_vol_ann = np.std(port) * np.sqrt(252)
    bench_vol_ann = np.std(bench) * np.sqrt(252)
    
    # Ratio de Sharpe
    port_sharpe = (port_return_ann - risk_free_rate) / port_vol_ann if port_vol_ann != 0 else 0
    bench_sharpe = (bench_return_ann - risk_free_rate) / bench_vol_ann if bench_vol_ann != 0 else 0
    
    # Drawdown
    port_cum = (1 + port).cumprod()
    bench_cum = (1 + bench).cumprod()
    
    port_dd = ((port_cum - port_cum.cummax()) / port_cum.cummax()).min()
    bench_dd = ((bench_cum - bench_cum.cummax()) / bench_cum.cummax()).min()
    
    # Rendement total sur la période
    port_total = port_cum.iloc[-1] - 1
    bench_total = bench_cum.iloc[-1] - 1
    
    return {
        "portfolio": {
            "return_ann": port_return_ann,
            "volatility_ann": port_vol_ann,
            "sharpe": port_sharpe,
            "max_drawdown": port_dd,
            "total_return": port_total,
        },
        "benchmark": {
            "return_ann": bench_return_ann,
            "volatility_ann": bench_vol_ann,
            "sharpe": bench_sharpe,
            "max_drawdown": bench_dd,
            "total_return": bench_total,
        },
        "alpha": ab['alpha'] if ab else 0,
        "beta": ab['beta'] if ab else 0,
        "tracking_error": te,
        "information_ratio": ir,
        "up_capture": capture['up_capture'],
        "down_capture": capture['down_capture'],
        "excess_return": port_return_ann - bench_return_ann,
    }


def print_benchmark_report(metrics, benchmark_name="S&P 500"):
    """
    Affiche un rapport de comparaison avec le benchmark
    """
    print("=" * 80)
    print(f"📊 COMPARAISON AVEC LE BENCHMARK : {benchmark_name}")
    print("=" * 80)
    print()
    
    p = metrics['portfolio']
    b = metrics['benchmark']
    
    print(f"{'Métrique':<30} {'Portefeuille':>18} {'Benchmark':>18} {'Écart':>15}")
    print("-" * 80)
    
    rows = [
        ("Rendement annualisé", p['return_ann'], b['return_ann'], True),
        ("Volatilité annualisée", p['volatility_ann'], b['volatility_ann'], True),
        ("Ratio de Sharpe", p['sharpe'], b['sharpe'], False),
        ("Max Drawdown", p['max_drawdown'], b['max_drawdown'], True),
        ("Rendement total", p['total_return'], b['total_return'], True),
    ]
    
    for label, p_val, b_val, is_pct in rows:
        if is_pct:
            p_str = f"{p_val*100:+.2f}%"
            b_str = f"{b_val*100:+.2f}%"
            ecart = f"{(p_val - b_val)*100:+.2f}%"
        else:
            p_str = f"{p_val:.3f}"
            b_str = f"{b_val:.3f}"
            ecart = f"{p_val - b_val:+.3f}"
        
        print(f"{label:<30} {p_str:>18} {b_str:>18} {ecart:>15}")
    
    print()
    print("=" * 80)
    print("📈 MÉTRIQUES DE COMPARAISON")
    print("=" * 80)
    print(f"  Alpha (annualisé)        : {metrics['alpha']*100:+.2f}%")
    print(f"  Beta                     : {metrics['beta']:.3f}")
    print(f"  Tracking Error           : {metrics['tracking_error']*100:.2f}%")
    print(f"  Information Ratio        : {metrics['information_ratio']:.3f}")
    print(f"  Up Capture Ratio         : {metrics['up_capture']:.1f}%")
    print(f"  Down Capture Ratio       : {metrics['down_capture']:.1f}%")
    print(f"  Rendement excédentaire   : {metrics['excess_return']*100:+.2f}%")
    print()
    
    # Interprétation
    print("=" * 80)
    print("💡 INTERPRÉTATION")
    print("=" * 80)
    
    if metrics['alpha'] > 0.02:
        print("✅ Alpha positif et significatif : le portefeuille surperforme le benchmark")
    elif metrics['alpha'] > 0:
        print("⚠️ Alpha légèrement positif : surperformance marginale")
    else:
        print("❌ Alpha négatif : sous-performance par rapport au benchmark")
    
    if metrics['beta'] < 0.5:
        print("✅ Beta faible : portefeuille peu corrélé au marché (bonne diversification)")
    elif metrics['beta'] < 1:
        print("⚠️ Beta modéré : portefeuille moins volatil que le marché")
    else:
        print("⚠️ Beta élevé : portefeuille plus volatil que le marché")
    
    if metrics['information_ratio'] > 0.5:
        print("✅ Information Ratio élevé : bonne gestion active")
    elif metrics['information_ratio'] > 0:
        print("⚠️ Information Ratio modéré")
    else:
        print("❌ Information Ratio négatif : gestion active inefficace")
    
    if metrics['down_capture'] < metrics['up_capture']:
        print("✅ Down Capture < Up Capture : le portefeuille résiste mieux aux baisses")
    
    print()


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from data_manager import load_portfolio
    from portfolio_optimizer import optimize_max_sharpe
    
    # Charger les données
    assets = ["BRVM_SNTS", "BRVM_ORAC", "BRVM_SGBC", "BRVM_ECOC"]
    prices = load_portfolio(assets)
    
    if prices is not None:
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Optimiser
        weights = optimize_max_sharpe(returns)
        portfolio_returns = returns.dot(weights)
        
        # Charger le benchmark (SPY)
        spy_prices = load_portfolio(["US_SPY"])
        
        if spy_prices is not None:
            spy_returns = np.log(spy_prices / spy_prices.shift(1)).dropna()['US_SPY']
            
            # Calculer les métriques
            metrics = calculate_all_benchmark_metrics(portfolio_returns, spy_returns)
            
            if metrics:
                print_benchmark_report(metrics, "S&P 500 (SPY)")
