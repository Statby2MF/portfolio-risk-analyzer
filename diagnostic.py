"""
Diagnostic pour vérifier les calculs de contribution et de beta
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import load_portfolio
from src.portfolio_optimizer import optimize_risk_parity, optimize_max_sharpe
from src.risk_contribution import calculate_risk_contribution


print("=" * 60)
print("🔍 DIAGNOSTIC")
print("=" * 60)

# ============================================================
# 1. TEST CONTRIBUTION AU RISQUE
# ============================================================
print("\n📊 TEST 1 : Contribution au risque\n")

assets = ['BRVM_ABJC', 'BRVM_BICC', 'BRVM_BNBC', 'BRVM_BOAB', 'BRVM_BOABF']
prices = load_portfolio(assets)

if prices is None:
    print("❌ Impossible de charger les données")
    sys.exit(1)

print(f"✅ {len(prices)} jours chargés")
print(f"   Actifs: {list(prices.columns)}")

returns = np.log(prices / prices.shift(1)).dropna()
print(f"✅ {len(returns)} rendements calculés")

weights = optimize_risk_parity(returns)
print(f"\n📊 Poids Risk Parity:")
for i, col in enumerate(returns.columns):
    print(f"   {col}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
print(f"   Somme: {sum(weights):.4f}")

# Test de la contribution
print(f"\n📊 Test calculate_risk_contribution:")
try:
    rc = calculate_risk_contribution(returns, np.array(weights).flatten())
    if rc:
        print("   ✅ Calcul réussi")
        print(f"   Volatilité portefeuille: {rc['portfolio_volatility']*100:.2f}%")
        print(f"\n   Contributions normalisées:")
        for i, col in enumerate(returns.columns):
            print(f"   {col}: {rc['risk_contribution_normalized'][i]:.2f}%")
    else:
        print("   ❌ rc = None")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# 2. TEST BETA
# ============================================================
print("\n" + "=" * 60)
print("📊 TEST 2 : Beta vs S&P 500")
print("=" * 60)

# Charger SPY
spy_prices = load_portfolio(['US_SPY'])

if spy_prices is None:
    print("❌ SPY non disponible")
else:
    print(f"✅ SPY: {len(spy_prices)} jours")
    print(f"   Période SPY: {spy_prices.index[0]} → {spy_prices.index[-1]}")
    
    # Portefeuille BRVM
    print(f"\n   Période BRVM: {prices.index[0]} → {prices.index[-1]}")
    
    # Calculer les rendements
    port_returns = returns.dot(weights)
    spy_returns = np.log(spy_prices / spy_prices.shift(1)).dropna()['US_SPY']
    
    # Normaliser les index
    port_idx = port_returns.index.normalize()
    spy_idx = spy_returns.index.normalize()
    
    port_returns.index = port_idx
    spy_returns.index = spy_idx
    
    # Supprimer doublons
    port_returns = port_returns[~port_returns.index.duplicated(keep='first')]
    spy_returns = spy_returns[~spy_returns.index.duplicated(keep='first')]
    
    # Intersection
    common = port_returns.index.intersection(spy_returns.index)
    print(f"\n📅 Dates communes: {len(common)}")
    
    if len(common) < 10:
        print("❌ Pas assez de dates communes")
        print(f"   Exemple BRVM: {port_returns.index[:3].tolist()}")
        print(f"   Exemple SPY: {spy_returns.index[:3].tolist()}")
    else:
        p = port_returns.loc[common]
        b = spy_returns.loc[common]
        
        # Beta
        cov = np.cov(p, b)[0, 1]
        var_b = np.var(b, ddof=1)
        beta = cov / var_b
        
        # Corrélation
        corr = np.corrcoef(p, b)[0, 1]
        
        # Alpha
        rf_daily = 0.02 / 252
        alpha_daily = np.mean(p) - rf_daily - beta * (np.mean(b) - rf_daily)
        alpha_ann = alpha_daily * 252
        
        print(f"\n📊 Résultats:")
        print(f"   Beta: {beta:.4f}")
        print(f"   Corrélation: {corr:.4f}")
        print(f"   Alpha annualisé: {alpha_ann*100:.2f}%")
        print(f"   Rendement portefeuille (commun): {np.mean(p)*252*100:.2f}%")
        print(f"   Rendement SPY (commun): {np.mean(b)*252*100:.2f}%")

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 60)
