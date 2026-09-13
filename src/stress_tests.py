"""
Stress tests : simulation de scénarios de crise
"""
import numpy as np
import pandas as pd


def scenario_market_crash(returns_df, weights, crash_pct=-0.20):
    """
    Scénario 1 : krach de marché global
    Tous les actifs baissent de X%
    """
    portfolio_return = crash_pct  # Tout baisse
    portfolio_loss = portfolio_return * 100
    
    return {
        "name": "Krach de marché",
        "description": f"Tous les actifs baissent de {crash_pct*100:.0f}%",
        "loss_pct": portfolio_loss,
        "loss_absolute": None,  # À calculer avec le capital
    }


def scenario_volatility_double(returns_df, weights):
    """
    Scénario 2 : volatilité × 2
    """
    portfolio_returns = returns_df.dot(weights)
    
    # Volatilité actuelle
    vol_actuelle = np.std(portfolio_returns) * np.sqrt(252)
    vol_stresse = vol_actuelle * 2
    
    # VaR à 95% sous stress (approximation)
    z_95 = 1.645
    var_stresse = -z_95 * vol_stresse / np.sqrt(252)
    
    return {
        "name": "Volatilité × 2",
        "description": "La volatilité double soudainement",
        "vol_actuelle": vol_actuelle,
        "vol_stressee": vol_stresse,
        "var_stressee": var_stresse * 100,
    }


def scenario_correlation_shock(returns_df, weights, correlation_increase=0.5):
    """
    Scénario 3 : augmentation des corrélations
    """
    # Corrélation actuelle
    corr_actuelle = returns_df.corr()
    
    # Corrélation stressée
    n = len(corr_actuelle)
    corr_stressee = corr_actuelle.copy()
    
    for i in range(n):
        for j in range(n):
            if i != j:
                # Augmenter les corrélations de X%
                nouvelle_corr = corr_actuelle.iloc[i, j] + correlation_increase * (1 - corr_actuelle.iloc[i, j])
                corr_stressee.iloc[i, j] = min(nouvelle_corr, 1.0)
    
    # Volatilité stressée
    vols = returns_df.std() * np.sqrt(252)
    cov_stressee = corr_stressee.values * np.outer(vols, vols)
    
    port_vol_stressee = np.sqrt(weights @ cov_stressee @ weights)
    port_vol_actuelle = np.sqrt(weights @ (returns_df.cov() * 252).values @ weights)
    
    return {
        "name": "Choc de corrélation",
        "description": f"Les corrélations augmentent de {correlation_increase*100:.0f}%",
        "vol_actuelle": port_vol_actuelle,
        "vol_stressee": port_vol_stressee,
        "augmentation": (port_vol_stressee / port_vol_actuelle - 1) * 100,
    }


def scenario_asset_crash(returns_df, weights, worst_asset_idx=None, crash_pct=-0.30):
    """
    Scénario 4 : effondrement du pire actif
    """
    n = len(returns_df.columns)
    
    if worst_asset_idx is None:
        # Prendre l'actif avec le plus grand poids
        worst_asset_idx = np.argmax(weights)
    
    worst_asset = returns_df.columns[worst_asset_idx]
    weight_worst = weights[worst_asset_idx]
    
    # Perte du portefeuille
    portfolio_loss = weight_worst * crash_pct * 100
    
    return {
        "name": f"Effondrement de {worst_asset}",
        "description": f"{worst_asset} baisse de {crash_pct*100:.0f}%",
        "asset": worst_asset,
        "weight": weight_worst,
        "loss_pct": portfolio_loss,
    }


def scenario_historical_crisis(returns_df, weights, crisis_start, crisis_end):
    """
    Scénario 5 : rejouer une crise historique
    """
    # Filtrer la période de crise
    try:
        crisis_returns = returns_df.loc[crisis_start:crisis_end]
        
        if len(crisis_returns) < 5:
            return None
        
        # Performance du portefeuille pendant la crise
        portfolio_returns = crisis_returns.dot(weights)
        cumulative = (1 + portfolio_returns).cumprod()
        
        total_return = cumulative.iloc[-1] - 1
        max_dd = ((cumulative - cumulative.cummax()) / cumulative.cummax()).min()
        vol = np.std(portfolio_returns) * np.sqrt(252)
        
        return {
            "name": "Crise historique",
            "description": f"Période {crisis_start} → {crisis_end}",
            "total_return": total_return * 100,
            "max_drawdown": max_dd * 100,
            "volatility": vol * 100,
            "n_days": len(crisis_returns),
        }
    except:
        return None


def run_all_stress_tests(returns_df, weights, capital=100000):
    """
    Exécute tous les stress tests
    """
    results = []
    
    # 1. Krach de marché
    crash = scenario_market_crash(returns_df, weights, crash_pct=-0.20)
    crash["loss_absolute"] = capital * crash["loss_pct"] / 100
    results.append(crash)
    
    # 2. Volatilité × 2
    vol = scenario_volatility_double(returns_df, weights)
    results.append(vol)
    
    # 3. Choc de corrélation
    corr = scenario_correlation_shock(returns_df, weights, correlation_increase=0.5)
    results.append(corr)
    
    # 4. Effondrement du pire actif
    asset_crash = scenario_asset_crash(returns_df, weights, crash_pct=-0.30)
    asset_crash["loss_absolute"] = capital * asset_crash["loss_pct"] / 100
    results.append(asset_crash)
    
    return results


def print_stress_report(results, capital=100000):
    """
    Affiche un rapport de stress tests
    """
    print("=" * 80)
    print("⚠️ STRESS TESTS")
    print("=" * 80)
    print(f"Capital initial : {capital:,.0f} FCFA")
    print()
    
    for r in results:
        print(f"🎯 {r['name']}")
        print(f"   {r['description']}")
        
        if "loss_pct" in r:
            print(f"   💰 Perte potentielle : {r['loss_pct']:.2f}%")
            if r.get("loss_absolute"):
                print(f"   💸 Perte en valeur : {r['loss_absolute']:,.0f} FCFA")
        
        if "var_stressee" in r:
            print(f"   📊 VaR 95% stressée : {r['var_stressee']:.2f}%")
            print(f"   📊 Volatilité stressée : {r['vol_stressee']*100:.2f}%")
        
        if "augmentation" in r:
            print(f"   📈 Augmentation de la volatilité : +{r['augmentation']:.1f}%")
        
        if "total_return" in r:
            print(f"   📉 Rendement pendant la crise : {r['total_return']:.2f}%")
            print(f"   📉 Max Drawdown : {r['max_drawdown']:.2f}%")
        
        print()
    
    # Bilan
    print("=" * 80)
    print("📊 BILAN")
    print("=" * 80)
    
    worst = min(results, key=lambda x: x.get("loss_pct", 0))
    print(f"❌ Pire scénario : {worst['name']} ({worst.get('loss_pct', 0):.2f}%)")
    print()


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.data_manager import load_portfolio
    from src.portfolio_optimizer import optimize_max_sharpe
    
    # Charger les données
    assets = ["BRVM_SNTS", "BRVM_ORAC", "BRVM_SGBC", "BRVM_ECOC"]
    prices = load_portfolio(assets)
    
    if prices is not None:
        returns = np.log(prices / prices.shift(1)).dropna()
        weights = optimize_max_sharpe(returns)
        
        # Stress tests
        results = run_all_stress_tests(returns, weights, capital=100000)
        print_stress_report(results, capital=100000)
