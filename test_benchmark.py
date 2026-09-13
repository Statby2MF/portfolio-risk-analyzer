"""
Test du module benchmark
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import load_portfolio
from src.portfolio_optimizer import optimize_max_sharpe
from src.benchmark import calculate_all_benchmark_metrics, print_benchmark_report

# Charger les données
assets = ["BRVM_SNTS", "BRVM_ORAC", "BRVM_SGBC", "BRVM_ECOC"]
print("📥 Chargement des données BRVM...")
prices = load_portfolio(assets)

if prices is None or prices.empty:
    print("❌ Impossible de charger les données")
    sys.exit(1)

print(f"✅ {len(prices)} jours de données chargées")
print(f"   Actifs : {list(prices.columns)}")

returns = np.log(prices / prices.shift(1)).dropna()
print(f"📊 Rendements calculés : {len(returns)} observations")

# Optimiser
print("\n🎯 Optimisation du portefeuille (Max Sharpe)...")
weights = optimize_max_sharpe(returns)
print(f"   Poids optimaux :")
for col, w in zip(returns.columns, weights):
    print(f"      {col}: {w:.2%}")

portfolio_returns = returns.dot(weights)

# Charger le benchmark
print("\n📥 Chargement du benchmark (SPY)...")
spy_prices = load_portfolio(["US_SPY"])

if spy_prices is None or spy_prices.empty:
    print("❌ Impossible de charger SPY")
    sys.exit(1)

print(f"✅ {len(spy_prices)} jours de SPY chargés")

spy_returns = np.log(spy_prices / spy_prices.shift(1)).dropna()['US_SPY']

# Calculer les métriques
print("\n📊 Calcul des métriques de benchmark...")
metrics = calculate_all_benchmark_metrics(portfolio_returns, spy_returns)

if metrics:
    print_benchmark_report(metrics, "S&P 500 (SPY)")
else:
    print("❌ Pas assez de données communes")
