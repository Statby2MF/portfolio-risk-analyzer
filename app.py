"""
Portfolio Risk Analyzer - Statby2mf
Dashboard professionnel avec identité visuelle
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import get_available_assets, load_portfolio
from src.risk_metrics import calculate_all_metrics
from src.portfolio_optimizer import get_optimal_portfolios, portfolio_return, portfolio_volatility, portfolio_sharpe

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Statby2mf | Portfolio Risk Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS - IDENTITÉ VISUELLE STATBY2MF
# ============================================================

st.markdown("""
<style>
    /* ===== FOND GLOBAL ===== */
    .stApp {
        background: linear-gradient(135deg, #0a3d2e 0%, #0d4a38 50%, #0a3d2e 100%);
        color: #f5f0e6;
    }
    
    /* ===== HEADER ===== */
    .main-header {
        background: linear-gradient(90deg, rgba(201,162,39,0.15) 0%, rgba(74,93,58,0.3) 100%);
        border: 1px solid rgba(201,162,39,0.4);
        border-radius: 20px;
        padding: 30px 40px;
        margin-bottom: 30px;
        backdrop-filter: blur(20px);
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #c9a227 0%, #f5f0e6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header .brand {
        color: #c9a227;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .main-header p {
        color: #d4c98a;
        font-size: 1rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    
    /* ===== CARTES MÉTRIQUES ===== */
    .metric-card {
        background: linear-gradient(135deg, rgba(74,93,58,0.5) 0%, rgba(10,61,46,0.7) 100%);
        border: 1px solid rgba(201,162,39,0.3);
        border-radius: 16px;
        padding: 22px 24px;
        transition: all 0.3s ease;
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
        background: linear-gradient(90deg, #c9a227, #9c9152);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(201,162,39,0.7);
        box-shadow: 0 12px 40px rgba(201,162,39,0.2);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        color: #d4c98a;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    
    .positive { color: #4ade80; }
    .negative { color: #f87171; }
    .neutral { color: #c9a227; }
    
    /* ===== SECTION TITLES ===== */
    .section-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-left: 16px;
        border-left: 4px solid #c9a227;
    }
    
    /* ===== SIDEBAR - CONTRASTES AMÉLIORÉS ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d4a38 0%, #0a3d2e 100%);
        border-right: 1px solid rgba(201,162,39,0.3);
    }
    
    /* Tous les textes de la sidebar */
    [data-testid="stSidebar"] * {
        color: #f5f0e6 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #c9a227 !important;
        font-weight: 700 !important;
    }
    
    /* Labels des inputs */
    [data-testid="stSidebar"] label {
        color: #d4c98a !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Radio buttons */
    [data-testid="stSidebar"] .stRadio label {
        color: #f5f0e6 !important;
        font-weight: 500 !important;
    }
    
    /* Multiselect */
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #d4c98a !important;
    }
    
    /* Messages d'info/warning/error dans la sidebar */
    [data-testid="stSidebar"] .stAlert {
        background: rgba(201,162,39,0.15) !important;
        border: 1px solid rgba(201,162,39,0.4) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stAlert p {
        color: #ffffff !important;
    }
    
    /* ===== BOUTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #c9a227 0%, #a88a1f 100%);
        color: #0a3d2e;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 700;
        font-size: 14px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(201,162,39,0.4);
        color: #0a3d2e;
    }
    
    /* ===== ONGLETS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(74,93,58,0.4);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: #d4c98a;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #c9a227 0%, #a88a1f 100%);
        color: #0a3d2e;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        color: #9c9152;
        font-size: 12px;
        padding: 40px 0 20px 0;
        margin-top: 40px;
        border-top: 1px solid rgba(201,162,39,0.2);
    }
    
    .footer .brand {
        color: #c9a227;
        font-weight: 700;
        letter-spacing: 2px;
    }
    
    /* ===== TEXTE GÉNÉRAL ===== */
    p, span, div {
        color: #f5f0e6;
    }
    
    /* ===== DATAFRAMES ===== */
    .dataframe {
        background: rgba(74,93,58,0.3) !important;
        color: #f5f0e6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class='main-header'>
    <div class='brand'>STATBY2MF</div>
    <h1>📊 Portfolio Risk Analyzer</h1>
    <p>Analyse professionnelle des risques · Marchés BRVM & US</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("<h3 style='color: #c9a227;'>⚙️ Configuration</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sélection du marché
    market = st.radio(
        "🌍 Marché",
        ["BRVM", "US", "Mixte"],
        index=0
    )
    
    st.markdown("---")
    
    # Actifs disponibles
    if market == "BRVM":
        available = get_available_assets("BRVM")
    elif market == "US":
        available = get_available_assets("US")
    else:
        available = get_available_assets("all")
    
    if not available:
        st.error("❌ Aucune donnée. Lancez `python download_data.py`")
        st.stop()
    
    # Sélection des actifs
    selected = st.multiselect(
        "📈 Actifs du portefeuille",
        available,
        default=available[:5] if len(available) >= 5 else available
    )
    
    if not selected:
        st.warning("Sélectionnez au moins un actif")
        st.stop()
    
    st.markdown("---")
    
    # Période
    period = st.selectbox(
        "📅 Période d'analyse",
        ["1 an", "2 ans", "3 ans", "5 ans", "Tout"],
        index=2
    )
    
    st.markdown("---")
    
    if st.button("🔄 Actualiser"):
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='color: #4a5d3a; font-size: 11px; text-align: center;'>
        <span style='color: #c9a227; font-weight: 700;'>STATBY2MF</span><br>
        ⚠️ Pas un conseil financier
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHARGEMENT
# ============================================================

period_days = {"1 an": 365, "2 ans": 730, "3 ans": 1095, "5 ans": 1825, "Tout": 5000}
start_date = datetime.now() - timedelta(days=period_days.get(period, 1095))

prices_df = load_portfolio(selected, start_date=start_date)

if prices_df is None or prices_df.empty:
    st.error("❌ Impossible de charger les données")
    st.stop()

returns_df = np.log(prices_df / prices_df.shift(1)).dropna()

# Recalculer n après alignement
n = len(returns_df.columns)
weights_eq = np.array([1/n] * n)
selected = list(returns_df.columns)

portfolio_returns = returns_df.dot(weights_eq)
portfolio_prices = (1 + portfolio_returns).cumprod() * 100

metrics = calculate_all_metrics(portfolio_returns, portfolio_prices)
portfolio_metrics = get_optimal_portfolios(returns_df)

# ============================================================
# MÉTRIQUES
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

tab1, tab2, tab3 = st.tabs(["📈 Performance", "⚠️ Risque", "🎯 Optimisation"])

with tab1:
    st.markdown("<div class='section-title'>📈 Évolution du portefeuille</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_prices.index,
        y=portfolio_prices.values,
        mode='lines',
        name='Portefeuille',
        line=dict(color='#c9a227', width=3),
        fill='tozeroy',
        fillcolor='rgba(201,162,39,0.1)'
    ))
    
    fig.update_layout(
        height=450,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(201,162,39,0.1)')
    )
    st.plotly_chart(fig, width='stretch')

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-title'>📊 Distribution</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=portfolio_returns,
            nbinsx=50,
            marker_color='#c9a227',
            opacity=0.8
        ))
        fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("<div class='section-title'>🔗 Corrélation</div>", unsafe_allow_html=True)
        corr = returns_df.corr()
        fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='YlOrBr', zmin=-1, zmax=1)
        fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')

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
                    <span style='color: #9c9152; font-size: 12px;'>Rendement:</span>
                    <span style='color: #10b981; font-weight: 700; float: right;'>{ret*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #9c9152; font-size: 12px;'>Volatilité:</span>
                    <span style='color: #ef4444; font-weight: 700; float: right;'>{vol*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #9c9152; font-size: 12px;'>Sharpe:</span>
                    <span style='color: #c9a227; font-weight: 700; float: right;'>{sharpe:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
<div class='footer'>
    <span class='brand'>STATBY2MF</span> · Portfolio Risk Analyzer<br>
    {datetime.now().strftime('%d/%m/%Y %H:%M')} · Données: BRVM & Yahoo Finance<br>
    ⚠️ Ceci n'est pas un conseil financier
</div>
""", unsafe_allow_html=True)
