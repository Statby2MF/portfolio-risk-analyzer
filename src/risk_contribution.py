"""
Décomposition de la contribution au risque par actif
"""
import numpy as np
import pandas as pd


def calculate_risk_contribution(returns_df, weights):
    """
    Calcule la contribution de chaque actif au risque total du portefeuille
    
    Formule :
    RC_i = w_i * (Σw)_i / sqrt(w'Σw)
    
    où Σ est la matrice de covariance
    """
    # Matrice de covariance annualisée
    cov = returns_df.cov() * 252
    
    # Volatilité du portefeuille
    port_var = weights.T @ cov @ weights
    port_vol = np.sqrt(port_var)
    
    # Contribution marginale
    marginal_contrib = cov @ weights
    
    # Contribution au risque (en valeur absolue)
    risk_contrib = weights * marginal_contrib / port_vol
    
    # Contribution en pourcentage
    risk_contrib_pct = risk_contrib / port_vol * 100
    
    # Contribution en pourcentage du total
    risk_contrib_normalized = risk_contrib_pct / risk_contrib_pct.sum() * 100
    
    return {
        "weights": weights,
        "risk_contribution": risk_contrib,
        "risk_contribution_pct": risk_contrib_pct,
        "risk_contribution_normalized": risk_contrib_normalized,
        "portfolio_volatility": port_vol,
    }


def contribution_table(returns_df, weights):
    """
    Retourne un DataFrame avec les contributions
    """
    rc = calculate_risk_contribution(returns_df, weights)
    
    df = pd.DataFrame({
        "Actif": returns_df.columns,
        "Poids (%)": rc['weights'] * 100,
        "Contribution au risque (%)": rc['risk_contribution_normalized'],
        "Ratio (contribution / poids)": rc['risk_contribution_normalized'] / (rc['weights'] * 100),
    })
    
    return df


def print_contribution_report(returns_df, weights, portfolio_name="Portefeuille"):
    """
    Affiche un rapport de contribution au risque
    """
    rc = calculate_risk_contribution(returns_df, weights)
    df = contribution_table(returns_df, weights)
    
    print("=" * 80)
    print(f"📊 CONTRIBUTION AU RISQUE - {portfolio_name}")
    print("=" * 80)
    print()
    print(f"Volatilité du portefeuille : {rc['portfolio_volatility']*100:.2f}%")
    print()
    
    print(f"{'Actif':<20} {'Poids':>12} {'Contribution':>15} {'Ratio':>12}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        actif = row['Actif']
        poids = row['Poids (%)']
        contrib = row['Contribution au risque (%)']
        ratio = row['Ratio (contribution / poids)']
        
        # Indicateur
        if ratio > 1.2:
            indicateur = "⚠️"
        elif ratio < 0.8:
            indicateur = "✅"
        else:
            indicateur = "⚪"
        
        print(f"{actif:<20} {poids:>11.2f}% {contrib:>14.2f}% {ratio:>11.2f} {indicateur}")
    
    print()
    print("=" * 80)
    print("💡 INTERPRÉTATION")
    print("=" * 80)
    
    for _, row in df.iterrows():
        actif = row['Actif']
        poids = row['Poids (%)']
        contrib = row['Contribution au risque (%)']
        ratio = row['Ratio (contribution / poids)']
        
        if ratio > 1.2:
            print(f"⚠️ {actif} : contribue {ratio:.2f}x plus au risque que son poids ({contrib:.1f}% vs {poids:.1f}%)")
            print(f"   → Cet actif est un AMPLIFICATEUR de risque")
        elif ratio < 0.8:
            print(f"✅ {actif} : contribue {ratio:.2f}x moins au risque que son poids ({contrib:.1f}% vs {poids:.1f}%)")
            print(f"   → Cet actif est un DIVERSIFICATEUR")
        else:
            print(f"⚪ {actif} : contribution équilibrée ({ratio:.2f}x)")
    
    print()
    
        # Vérifier si les contributions sont équilibrées
    # On regarde si les contributions sont proches les unes des autres
    contribs = df['Contribution au risque (%)'].values
    max_contrib = contribs.max()
    min_contrib = contribs.min()
    ecart_relatif = (max_contrib - min_contrib) / max_contrib * 100
    
    if ecart_relatif < 10:
        print("✅ Le portefeuille est BIEN ÉQUILIBRÉ (contributions proches)")
    elif ecart_relatif < 30:
        print("⚠️ Le portefeuille est MOYENNEMENT équilibré")
    else:
        print("❌ Le portefeuille est DÉSÉQUILIBRÉ (certains actifs dominent le risque)")
    
    print()
    
    return df


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.data_manager import load_portfolio
    from src.portfolio_optimizer import (
        optimize_max_sharpe,
        optimize_min_volatility,
        optimize_risk_parity,
    )
    
    # Charger les données
    assets = ["BRVM_SNTS", "BRVM_ORAC", "BRVM_SGBC", "BRVM_ECOC"]
    prices = load_portfolio(assets)
    
    if prices is not None:
        returns = np.log(prices / prices.shift(1)).dropna()
        
        # Analyser les 3 portefeuilles
        portfolios = {
            "Max Sharpe": optimize_max_sharpe(returns),
            "Min Volatilité": optimize_min_volatility(returns),
            "Risk Parity": optimize_risk_parity(returns),
        }
        
        for name, weights in portfolios.items():
            print_contribution_report(returns, weights, name)
            print("\n")
