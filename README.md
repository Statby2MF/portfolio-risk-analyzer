# 📊 Portfolio Risk Analyzer

**Analyse professionnelle des risques pour portefeuilles multi-actifs**

Développé par **Statby2mf**

---

## 🎯 Description

Portfolio Risk Analyzer est une application d'analyse quantitative complète qui permet d'évaluer, quantifier et optimiser le risque d'un portefeuille d'investissement.

Le projet intègre les modèles les plus avancés de la théorie financière moderne :

- **Mesures de risque** : VaR historique, paramétrique, Cornish-Fisher
- **Théorie des valeurs extrêmes** : Expected Shortfall (ES 95%, ES 99%)
- **Optimisation de portefeuille** : Markowitz (Max Sharpe, Min Volatilité, Risk Parity)
- **Validation rigoureuse** : In-sample / Out-of-sample, Walk-forward
- **Analyse benchmark** : Alpha, Beta, Information Ratio, Tracking Error
- **Stress tests** : 4 scénarios de crise
- **Décomposition du risque** : Contribution par actif

---

## ✨ Fonctionnalités

### 📈 Analyse de performance
- Rendement annualisé
- Volatilité
- Ratios de Sharpe et Sortino
- Max Drawdown
- Skewness et Kurtosis

### ⚠️ Mesures de risque
- VaR 95% et 99% (3 méthodes)
- Expected Shortfall 95% et 99%
- Matrice de corrélation

### 🎯 Optimisation
- **Max Sharpe** : meilleur ratio rendement/risque
- **Min Volatilité** : portefeuille le moins risqué
- **Risk Parity** : contribution équilibrée au risque

### 🔬 Validation
- In-sample (70%) / Out-of-sample (30%)
- Walk-forward analysis
- Détection de sur-apprentissage

### 📊 Benchmark
- Comparaison avec le S&P 500
- Alpha, Beta, Information Ratio
- Up/Down Capture Ratio

### 💥 Stress Tests
- Krach de marché (-20%)
- Volatilité × 2
- Choc de corrélation (+50%)
- Effondrement du pire actif

### 📄 Rapport PDF
- Rapport professionnel automatique
- 3 pages denses et complètes

---

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Statby2Mf/portfolio-risk-analyzer.git
cd portfolio-risk-analyzer
