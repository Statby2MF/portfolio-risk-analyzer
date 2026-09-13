"""
Portfolio Risk Analyzer - Statby2mf
Dashboard professionnel complet avec rapport PDF
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_manager import get_available_assets, load_portfolio
from src.risk_metrics import calculate_all_metrics
from src.portfolio_optimizer import (
    get_optimal_portfolios,
    portfolio_return,
    portfolio_volatility,
    portfolio_sharpe,
)
from src.validation import in_out_validation, walk_forward_validation
from src.benchmark import calculate_all_benchmark_metrics
from src.stress_tests import run_all_stress_tests
from src.risk_contribution import calculate_risk_contribution
from src.report_generator import generate_pdf_report


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
# CSS
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a3d2e 0%, #0d4a38 50%, #0a3d2e 100%);
        color: #f5f0e6;
    }
    
    .main-header {
        background: linear-gradient(90deg, rgba(201,162,39,0.15) 0%, rgba(74,93,58,0.3) 100%);
        border: 1px solid rgba(201,162,39,0.4);
        border-radius: 20px;
        padding: 30px 40px;
        margin-bottom: 30px;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #c9a227 0%, #f5f0e6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
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
        margin-top: 8px;
        margin-bottom: 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(74,93,58,0.5) 0%, rgba(10,61,46,0.7) 100%);
        border: 1px solid rgba(201,162,39,0.3);
        border-radius: 16px;
        padding: 22px 24px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(201,162,39,0.7);
        box-shadow: 0 12px 40px rgba(201,162,39,0.2);
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
    }
    
    .section-title {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-left: 16px;
        border-left: 4px solid #c9a227;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d4a38 0%, #0a3d2e 100%);
        border-right: 1px solid rgba(201,162,39,0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #f5f0e6 !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #c9a227 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #d4c98a !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .stAlert {
        background: rgba(201,162,39,0.15) !important;
        border: 1px solid rgba(201,162,39,0.4) !important;
    }
    
    [data-testid="stSidebar"] .stAlert p {
        color: #ffffff !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #c9a227 0%, #a88a1f 100%);
        color: #0a3d2e;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 700;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(201,162,39,0.4);
        color: #0a3d2e;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        color: #0a3d2e;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 700;
        width: 100%;
    }
    
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
    
    p, span, div { color: #f5f0e6; }
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
    
    market = st.radio("🌍 Marché", ["BRVM", "US", "Mixte"], index=0)
    
    st.markdown("---")
    
    if market == "BRVM":
        available = get_available_assets("BRVM")
    elif market == "US":
        available = get_available_assets("US")
    else:
        available = get_available_assets("all")
    
    if not available:
        st.error("❌ Aucune donnée. Lancez `python download_data.py`")
        st.stop()
    
    selected = st.multiselect(
        "📈 Actifs du portefeuille",
        available,
        default=available[:5] if len(available) >= 5 else available
    )
    
    if not selected:
        st.warning("Sélectionnez au moins un actif")
        st.stop()
    
    st.markdown("---")
    
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

n = len(returns_df.columns)
weights_eq = np.array([1/n] * n)
selected = list(returns_df.columns)

portfolio_returns = returns_df.dot(weights_eq)
portfolio_prices = (1 + portfolio_returns).cumprod() * 100

metrics = calculate_all_metrics(portfolio_returns, portfolio_prices)
portfolio_metrics = get_optimal_portfolios(returns_df)


# ============================================================
# BOUTON RAPPORT PDF
# ============================================================

st.markdown("<div class='section-title'>📄 Rapport d'analyse</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("📄 Générer le rapport PDF"):
        with st.spinner("Génération du PDF en cours..."):
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
                
                st.session_state['pdf_buffer'] = pdf_buffer.getvalue()
                st.success("✅ Rapport généré !")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

with col2:
    if 'pdf_buffer' in st.session_state:
        st.download_button(
            label="📥 Télécharger le rapport PDF",
            data=st.session_state['pdf_buffer'],
            file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("💡 Cliquez sur 'Générer le rapport' pour créer votre PDF personnalisé")


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
        <div class='metric-value' style='color: #f87171;'>{var*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    es = metrics['es_99']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>ES 99%</div>
        <div class='metric-value' style='color: #f87171;'>{es*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    dd = metrics['max_drawdown']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Max Drawdown</div>
        <div class='metric-value' style='color: #f87171;'>{dd*100:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ONGLETS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Performance",
    "⚠️ Risque",
    "🎯 Optimisation",
    "🔬 Validation",
    "📊 Benchmark",
    "💥 Stress Tests",
    "📉 Contribution",
])


# ===== TAB 1 : PERFORMANCE =====
with tab1:
    st.markdown("<div class='section-title'>📈 Évolution du portefeuille</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_prices.index, y=portfolio_prices.values,
        mode='lines', name='Portefeuille',
        line=dict(color='#c9a227', width=3),
        fill='tozeroy', fillcolor='rgba(201,162,39,0.1)'
    ))
    fig.update_layout(
        height=450, template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified', margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(201,162,39,0.1)')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='section-title'>📊 Comparaison des actifs</div>", unsafe_allow_html=True)
    
    normalized = prices_df / prices_df.iloc[0] * 100
    fig = go.Figure()
    colors = ['#c9a227', '#4ade80', '#60a5fa', '#f87171', '#a78bfa', '#fb923c', '#34d399', '#f472b6']
    for i, col in enumerate(normalized.columns):
        fig.add_trace(go.Scatter(
            x=normalized.index, y=normalized[col],
            mode='lines', name=col,
            line=dict(width=2, color=colors[i % len(colors)])
        ))
    fig.update_layout(
        height=400, template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified', margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


# ===== TAB 2 : RISQUE =====
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-title'>📊 Distribution</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=portfolio_returns, nbinsx=50,
                                   marker_color='#c9a227', opacity=0.8))
        fig.add_vline(x=metrics['var_99_historique'], line_dash="dash",
                      line_color="#f87171", annotation_text="VaR 99%")
        fig.update_layout(height=400, template='plotly_dark',
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<div class='section-title'>🔗 Corrélation</div>", unsafe_allow_html=True)
        corr = returns_df.corr()
        fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='YlOrBr', zmin=-1, zmax=1)
        fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='section-title'>📋 Métriques de risque</div>", unsafe_allow_html=True)
    
    risk_df = pd.DataFrame([
        {"Métrique": "Volatilité annualisée", "Valeur": f"{metrics['volatilite_annuelle']*100:.2f}%"},
        {"Métrique": "VaR 95% (historique)", "Valeur": f"{metrics['var_95_historique']*100:.2f}%"},
        {"Métrique": "VaR 99% (historique)", "Valeur": f"{metrics['var_99_historique']*100:.2f}%"},
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
                    <span style='color: #d4c98a; font-size: 12px;'>Rendement:</span>
                    <span style='color: #4ade80; font-weight: 700; float: right;'>{ret*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #d4c98a; font-size: 12px;'>Volatilité:</span>
                    <span style='color: #f87171; font-weight: 700; float: right;'>{vol*100:.2f}%</span>
                </div>
                <div style='margin-top: 6px;'>
                    <span style='color: #d4c98a; font-size: 12px;'>Sharpe:</span>
                    <span style='color: #c9a227; font-weight: 700; float: right;'>{sharpe:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>📊 Allocation par portefeuille</div>", unsafe_allow_html=True)
    
    fig = go.Figure()
    for name, weights in portfolios.items():
        fig.add_trace(go.Bar(
            name=name, x=selected, y=weights * 100,
            text=[f"{w*100:.1f}%" for w in weights],
            textposition='outside'
        ))
    fig.update_layout(
        barmode='group', height=400, template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Allocation (%)", margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


# ===== TAB 4 : VALIDATION =====
with tab4:
    st.markdown("<div class='section-title'>🔬 Validation In-Sample / Out-of-Sample</div>", unsafe_allow_html=True)
    
    with st.spinner("Calcul de la validation..."):
        try:
            val_results, train, test = in_out_validation(returns_df, train_ratio=0.7)
            
            st.markdown(f"**In-Sample** : {train.index[0].strftime('%Y-%m-%d')} → {train.index[-1].strftime('%Y-%m-%d')} ({len(train)} jours)")
            st.markdown(f"**Out-of-Sample** : {test.index[0].strftime('%Y-%m-%d')} → {test.index[-1].strftime('%Y-%m-%d')} ({len(test)} jours)")
            st.markdown("---")
            
            for name, res in val_results.items():
                st.markdown(f"### 🎯 {name}")
                
                in_s = res['in_sample']
                out_s = res['out_of_sample']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sharpe In-Sample", f"{in_s['sharpe']:.3f}")
                with col2:
                    st.metric("Sharpe Out-of-Sample", f"{out_s['sharpe']:.3f}")
                with col3:
                    st.metric("Ratio Out/In", f"{res['sharpe_ratio_out_in']:.2f}")
                
                ratio = res['sharpe_ratio_out_in']
                if ratio > 0.7:
                    st.success("✅ Modèle ROBUSTE (peu de sur-apprentissage)")
                elif ratio > 0.4:
                    st.warning("⚠️ Modèle MOYENNEMENT robuste")
                else:
                    st.error("❌ Modèle a probablement SUR-APPRIS")
                
                st.markdown("---")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")


# ===== TAB 5 : BENCHMARK =====
with tab5:
    st.markdown("<div class='section-title'>📊 Comparaison avec le benchmark</div>", unsafe_allow_html=True)
    
    with st.spinner("Calcul du benchmark..."):
        try:
            spy_prices = load_portfolio(["US_SPY"])
            
            if spy_prices is not None and not spy_prices.empty:
                spy_returns = np.log(spy_prices / spy_prices.shift(1)).dropna()['US_SPY']
                weights = portfolio_metrics['max_sharpe']
                port_returns = returns_df.dot(weights)
                
                bench_metrics = calculate_all_benchmark_metrics(port_returns, spy_returns)
                
                if bench_metrics:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Portefeuille")
                        st.metric("Rendement annualisé", f"{bench_metrics['portfolio']['return_ann']*100:+.2f}%")
                        st.metric("Volatilité", f"{bench_metrics['portfolio']['volatility_ann']*100:.2f}%")
                        st.metric("Sharpe", f"{bench_metrics['portfolio']['sharpe']:.3f}")
                    
                    with col2:
                        st.markdown("### S&P 500")
                        st.metric("Rendement annualisé", f"{bench_metrics['benchmark']['return_ann']*100:+.2f}%")
                        st.metric("Volatilité", f"{bench_metrics['benchmark']['volatility_ann']*100:.2f}%")
                        st.metric("Sharpe", f"{bench_metrics['benchmark']['sharpe']:.3f}")
                    
                    st.markdown("---")
                    st.markdown("### Métriques de comparaison")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Alpha", f"{bench_metrics['alpha']*100:+.2f}%")
                    with col2:
                        st.metric("Beta", f"{bench_metrics['beta']:.3f}")
                    with col3:
                        st.metric("Information Ratio", f"{bench_metrics['information_ratio']:.3f}")
                    with col4:
                        st.metric("Tracking Error", f"{bench_metrics['tracking_error']*100:.2f}%")
                else:
                    st.warning("Pas assez de données communes")
            else:
                st.warning("SPY non disponible")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")


# ===== TAB 6 : STRESS TESTS =====
with tab6:
    st.markdown("<div class='section-title'>💥 Stress Tests</div>", unsafe_allow_html=True)
    
    try:
        weights = portfolio_metrics['max_sharpe']
        results = run_all_stress_tests(returns_df, weights, capital=100000)
        
        for r in results:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"### {r['name']}")
            with col2:
                st.markdown(f"*{r['description']}*")
                if "loss_pct" in r:
                    st.metric("Perte potentielle", f"{r['loss_pct']:.2f}%",
                              f"{r.get('loss_absolute', 0):,.0f} FCFA")
                if "var_stressee" in r:
                    st.metric("VaR 95% stressée", f"{r['var_stressee']:.2f}%")
                if "augmentation" in r:
                    st.metric("Augmentation volatilité", f"+{r['augmentation']:.1f}%")
            st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur: {e}")


# ===== TAB 7 : CONTRIBUTION =====
with tab7:
    st.markdown("<div class='section-title'>📉 Contribution au risque</div>", unsafe_allow_html=True)
    
    try:
        weights = portfolio_metrics['risk_parity']
        rc = calculate_risk_contribution(returns_df, weights)
        
        contrib_df = pd.DataFrame({
            "Actif": selected,
            "Poids (%)": rc['weights'] * 100,
            "Contribution au risque (%)": rc['risk_contribution_normalized'],
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Poids", x=contrib_df['Actif'],
                             y=contrib_df['Poids (%)'], marker_color='#c9a227'))
        fig.add_trace(go.Bar(name="Contribution", x=contrib_df['Actif'],
                             y=contrib_df['Contribution au risque (%)'],
                             marker_color='#f87171'))
        fig.update_layout(
            barmode='group', height=400, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="%", margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(contrib_df, use_container_width=True, hide_index=True)
        st.markdown(f"**Volatilité du portefeuille** : {rc['portfolio_volatility']*100:.2f}%")
    except Exception as e:
        st.error(f"❌ Erreur: {e}")


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
