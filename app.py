"""
Portfolio Risk Analyzer - Dashboard Professionnel
Analyse de risque pour portefeuille multi-actifs
"""
from src.report_generator import generate_pdf_report
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import get_available_assets, load_portfolio, load_returns
from src.risk_metrics import calculate_all_metrics, calculate_returns, calculate_max_drawdown
from src.portfolio_optimizer import get_optimal_portfolios, portfolio_return, portfolio_volatility, portfolio_sharpe


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Portfolio Risk Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PREMIUM - DESIGN PROFESSIONNEL
# ============================================================

st.markdown("""
<style>
    /* ===== FOND GLOBAL ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1429 100%);
        color: #e4e4e7;
    }
    
    /* ===== HEADER ===== */
    .main-header {
        background: linear-gradient(90deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 100%);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 20px;
        padding: 30px 40px;
        margin-bottom: 30px;
        backdrop-filter: blur(20px);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header p {
        color: #9ca3af;
        font-size: 1rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    
    /* ===== CARTES MÉTRIQUES ===== */
    .metric-card {
        background: linear-gradient(135deg, rgba(30,35,60,0.8) 0%, rgba(20,25,45,0.8) 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 22px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99,102,241,0.5);
        box-shadow: 0 12px 40px rgba(99,102,241,0.15);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        color: #9ca3af;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    
    .metric-delta {
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .neutral { color: #f59e0b; }
    
    /* ===== SECTION TITLES ===== */
    .section-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-left: 16px;
        border-left: 4px solid #6366f1;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1429 0%, #0a0e27 100%);
        border-right: 1px solid rgba(99,102,241,0.15);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }
    
    /* ===== BOUTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(99,102,241,0.3);
    }
    
    /* ===== TABLES ===== */
    .dataframe {
        background: rgba(30,35,60,0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
    }
    
    /* ===== ONGLETS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30,35,60,0.5);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: #9ca3af;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        color: #4b5563;
        font-size: 12px;
        padding: 40px 0 20px 0;
        margin-top: 40px;
        border-top: 1px solid rgba(99,102,241,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class='main-header'>
    <h1>📊 Portfolio Risk Analyzer</h1>
    <p>Analyse professionnelle des risques pour portefeuille multi-actifs</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # Actifs disponibles
    available = get_available_assets()
    
    if not available:
        st.error("❌ Aucune donnée. Lancez `python download_data.py`")
        st.stop()
    
    selected = st.multiselect(
        "📈 Actifs du portefeuille",
        available,
        default=available[:4] if len(available) >= 4 else available
    )
    
    if not selected:
        st.warning("Sélectionnez au moins un actif")
        st.stop()
    
    st.markdown("---")
    st.markdown("### 📅 Période")
    
    period = st.selectbox(
        "Fenêtre d'analyse",
        ["6 mois", "1 an", "2 ans", "Tout"],
        index=1
    )
    
    st.markdown("---")
    
    if st.button("🔄 Actualiser"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='color: #6b7280; font-size: 11px; text-align: center;'>
        ⚠️ Ceci n'est pas un conseil financier
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

# Filtrer par période
from datetime import timedelta
period_days = {"6 mois": 180, "1 an": 365, "2 ans": 730, "Tout": 3650}
start_date = datetime.now() - timedelta(days=period_days.get(period, 730))

prices_df = load_portfolio(selected, start_date=start_date)

if prices_df is None or prices_df.empty:
    st.error("❌ Impossible de charger les données")
    st.stop()

returns_df = np.log(prices_df / prices_df.shift(1)).dropna()

# Recalculer n APRÈS l'alignement des dates
n = len(returns_df.columns)
weights_eq = np.array([1/n] * n)

# Mettre à jour la liste des actifs réellement utilisés
selected = list(returns_df.columns)

portfolio_returns = returns_df.dot(weights_eq)
portfolio_prices = (1 + portfolio_returns).cumprod() * 100
# Calcul des métriques
metrics = calculate_all_metrics(portfolio_returns, portfolio_prices)
portfolio_metrics = get_optimal_portfolios(returns_df)
# Bouton rapport PDF (maintenant que metrics est défini)
if st.button("📄 Générer le rapport PDF"):
    with st.spinner("Génération du PDF..."):
        try:
            pdf_buffer = io.BytesIO()
            
            generate_pdf_report(
                pdf_buffer,
                "Portefeuille Multi-Actifs",
                selected,
                metrics,
                prices_df,
                returns_df,
                portfolio_metrics,
                portfolio_returns,
                portfolio_prices
            )
            
            pdf_buffer.seek(0)
            
            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf_buffer,
                file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
            
            st.success("✅ Rapport généré avec succès !")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
# ============================================================
# MÉTRIQUES PRINCIPALES
# ============================================================

st.markdown("<div class='section-title'>📊 Vue d'ensemble</div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    ret = metrics['rendement_annualise']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Rendement annualisé</div>
        <div class='metric-value'>{ret*100:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    vol = metrics['volatilite_annuelle']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Volatilité</div>
        <div class='metric-value'>{vol*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    var = metrics['var_99_historique']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>VaR 99%</div>
        <div class='metric-value negative'>{var*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    es = metrics['es_99']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Expected Shortfall 99%</div>
        <div class='metric-value negative'>{es*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    dd = metrics['max_drawdown']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Max Drawdown</div>
        <div class='metric-value negative'>{dd*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ONGLETS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "⚠️ Risque", "🎯 Optimisation", "📋 Détails"])

# ===== TAB 1 : PERFORMANCE =====
with tab1:
    st.markdown("<div class='section-title'>📈 Évolution du portefeuille</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_prices.index,
        y=portfolio_prices.values,
        mode='lines',
        name='Portefeuille',
        line=dict(color='#6366f1', width=3),
        fill='tozeroy',
        fillcolor='rgba(99,102,241,0.1)'
    ))
    
    fig.update_layout(
        height=450,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(99,102,241,0.1)')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparaison avec les actifs individuels
    st.markdown("<div class='section-title'>📊 Comparaison des actifs</div>", unsafe_allow_html=True)
    
    normalized = prices_df / prices_df.iloc[0] * 100
    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode='lines',
            name=col,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


# ===== TAB 2 : RISQUE =====
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-title'>📊 Distribution des rendements</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=portfolio_returns,
            nbinsx=50,
            marker_color='#6366f1',
            opacity=0.8
        ))
        fig.add_vline(
            x=metrics['var_99_historique'],
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="VaR 99%"
        )
        fig.update_layout(
            height=400,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<div class='section-title'>🔗 Matrice de corrélation</div>", unsafe_allow_html=True)
        corr = returns_df.corr()
        fig = px.imshow(
            corr,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            aspect='auto'
        )
        fig.update_layout(
            height=400,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques détaillées
    st.markdown("<div class='section-title'>📋 Statistiques de risque</div>", unsafe_allow_html=True)
    
    risk_df = pd.DataFrame([
        {"Métrique": "Volatilité annualisée", "Valeur": f"{metrics['volatilite_annuelle']*100:.2f}%"},
        {"Métrique": "VaR 95% (historique)", "Valeur": f"{metrics['var_95_historique']*100:.2f}%"},
        {"Métrique": "VaR 99% (historique)", "Valeur": f"{metrics['var_99_historique']*100:.2f}%"},
        {"Métrique": "VaR 95% (paramétrique)", "Valeur": f"{metrics['var_95_parametrique']*100:.2f}%"},
        {"Métrique": "VaR 99% (paramétrique)", "Valeur": f"{metrics['var_99_parametrique']*100:.2f}%"},
        {"Métrique": "VaR 95% (Cornish-Fisher)", "Valeur": f"{metrics['var_95_cornish_fisher']*100:.2f}%"},
        {"Métrique": "VaR 99% (Cornish-Fisher)", "Valeur": f"{metrics['var_99_cornish_fisher']*100:.2f}%"},
        {"Métrique": "Expected Shortfall 95%", "Valeur": f"{metrics['es_95']*100:.2f}%"},
        {"Métrique": "Expected Shortfall 99%", "Valeur": f"{metrics['es_99']*100:.2f}%"},
        {"Métrique": "Max Drawdown", "Valeur": f"{metrics['max_drawdown']*100:.2f}%"},
        {"Métrique": "Ratio de Sharpe", "Valeur": f"{metrics['sharpe']:.2f}"},
        {"Métrique": "Ratio de Sortino", "Valeur": f"{metrics['sortino']:.2f}"},
        {"Métrique": "Skewness", "Valeur": f"{metrics['skewness']:.3f}"},
        {"Métrique": "Kurtosis", "Valeur": f"{metrics['kurtosis']:.3f}"},
    ])
    st.dataframe(risk_df, use_container_width=True, hide_index=True)


# ===== TAB 3 : OPTIMISATION =====
with tab3:
    st.markdown("<div class='section-title'>🎯 Portefeuilles optimaux</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    portfolios = {
        "Max Sharpe": portfolio_metrics['max_sharpe'],
        "Min Volatilité": portfolio_metrics['min_volatility'],
        "Risk Parity": portfolio_metrics['risk_parity'],
    }
    
    for idx, (name, weights) in enumerate(portfolios.items()):
        with [col1, col2, col3][idx]:
            ret = portfolio_return(returns_df, weights)
            vol = portfolio_volatility(returns_df, weights)
            sharpe = portfolio_sharpe(returns_df, weights)
            
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{name}</div>
                <div style='margin-top: 12px;'>
                    <span style='color: #9ca3af; font-size: 12px;'>Rendement:</span>
                    <span style='color: #10b981; font-weight: 700; float: right;'>{ret*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #9ca3af; font-size: 12px;'>Volatilité:</span>
                    <span style='color: #f59e0b; font-weight: 700; float: right;'>{vol*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #9ca3af; font-size: 12px;'>Sharpe:</span>
                    <span style='color: #6366f1; font-weight: 700; float: right;'>{sharpe:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Graphique des allocations
    st.markdown("<div class='section-title'>📊 Allocation par portefeuille</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    for name, weights in portfolios.items():
        fig.add_trace(go.Bar(
            name=name,
            x=selected,
            y=weights * 100,
            text=[f"{w*100:.1f}%" for w in weights],
            textposition='outside'
        ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Allocation (%)",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


# ===== TAB 4 : DÉTAILS =====
with tab4:
    st.markdown("<div class='section-title'>📋 Données brutes</div>", unsafe_allow_html=True)
    
    st.markdown("**Prix**")
    st.dataframe(prices_df.tail(20), use_container_width=True)
    
    st.markdown("**Rendements**")
    st.dataframe(returns_df.tail(20), use_container_width=True)
    
    st.markdown("**Statistiques par actif**")
    stats_df = pd.DataFrame({
        "Rendement annualisé": returns_df.mean() * 252 * 100,
        "Volatilité annualisée": returns_df.std() * np.sqrt(252) * 100,
        "Sharpe": (returns_df.mean() * 252 - 0.02) / (returns_df.std() * np.sqrt(252)),
    }).round(2)
    st.dataframe(stats_df, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
<div class='footer'>
    📊 Portfolio Risk Analyzer · {datetime.now().strftime('%d/%m/%Y %H:%M')} · 
    Données: CoinGecko / Yahoo Finance / BRVM · ⚠️ Ceci n'est pas un conseil financier
</div>
""", unsafe_allow_html=True)
