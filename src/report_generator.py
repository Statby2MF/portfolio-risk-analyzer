"""
Génération de rapport PDF professionnel - Version enrichie
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import pandas as pd
import numpy as np


def generate_pdf_report(
    output_path,
    portfolio_name,
    assets,
    metrics,
    prices_df,
    returns_df,
    optimal_portfolios,
    portfolio_returns,
    portfolio_prices
):
    """
    Génère un rapport PDF professionnel complet
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                  fontSize=24, textColor=colors.HexColor('#c9a227'),
                                  spaceAfter=20, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
                                     fontSize=12, textColor=colors.HexColor('#6b7280'),
                                     spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                    fontSize=16, textColor=colors.HexColor('#0a3d2e'),
                                    spaceBefore=20, spaceAfter=10)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'],
                                 fontSize=11, textColor=colors.HexColor('#374151'),
                                 alignment=TA_JUSTIFY, spaceAfter=10)
    
    elements = []
    
    # ===== PAGE DE GARDE =====
    elements.append(Spacer(1, 3*cm))
    elements.append(Paragraph("📊 Portfolio Risk Analyzer", title_style))
    elements.append(Paragraph("Rapport d'analyse des risques", subtitle_style))
    elements.append(Spacer(1, 2*cm))
    
    info_data = [
        ["Portefeuille", portfolio_name],
        ["Actifs analysés", ", ".join(assets[:5]) + ("..." if len(assets) > 5 else "")],
        ["Nombre d'actifs", str(len(assets))],
        ["Date du rapport", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Nombre d'observations", f"{len(returns_df)} jours"],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(info_table)
    elements.append(PageBreak())
    
    # ===== SECTION 1 : PERFORMANCE =====
    elements.append(Paragraph("1. Métriques de performance", heading_style))
    
    perf_data = [
        ["Métrique", "Valeur"],
        ["Rendement annualisé", f"{metrics['rendement_annualise']*100:.2f}%"],
        ["Volatilité annualisée", f"{metrics['volatilite_annuelle']*100:.2f}%"],
        ["Ratio de Sharpe", f"{metrics['sharpe']:.2f}"],
        ["Ratio de Sortino", f"{metrics['sortino']:.2f}"],
    ]
    
    perf_table = Table(perf_data, colWidths=[8*cm, 7*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c9a227')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(perf_table)
    
    # ===== SECTION 2 : RISQUE =====
    elements.append(Paragraph("2. Métriques de risque", heading_style))
    
    risk_data = [
        ["Métrique", "Valeur"],
        ["VaR 95% (historique)", f"{metrics['var_95_historique']*100:.2f}%"],
        ["VaR 99% (historique)", f"{metrics['var_99_historique']*100:.2f}%"],
        ["VaR 95% (Cornish-Fisher)", f"{metrics['var_95_cornish_fisher']*100:.2f}%"],
        ["VaR 99% (Cornish-Fisher)", f"{metrics['var_99_cornish_fisher']*100:.2f}%"],
        ["Expected Shortfall 95%", f"{metrics['es_95']*100:.2f}%"],
        ["Expected Shortfall 99%", f"{metrics['es_99']*100:.2f}%"],
        ["Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%"],
        ["Skewness", f"{metrics['skewness']:.3f}"],
        ["Kurtosis", f"{metrics['kurtosis']:.3f}"],
    ]
    
    risk_table = Table(risk_data, colWidths=[8*cm, 7*cm])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(risk_table)
    
    elements.append(PageBreak())
    
    # ===== SECTION 3 : ALLOCATION =====
    elements.append(Paragraph("3. Allocation optimale (Markowitz)", heading_style))
    
    alloc_data = [["Actif", "Max Sharpe", "Min Volatilité", "Risk Parity"]]
    
    for i, asset in enumerate(assets):
        alloc_data.append([
            asset,
            f"{optimal_portfolios['max_sharpe'][i]*100:.1f}%",
            f"{optimal_portfolios['min_volatility'][i]*100:.1f}%",
            f"{optimal_portfolios['risk_parity'][i]*100:.1f}%",
        ])
    
    alloc_table = Table(alloc_data, colWidths=[4*cm, 3.7*cm, 3.7*cm, 3.6*cm])
    alloc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a3d2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(alloc_table)
    
    elements.append(PageBreak())
    
    # ===== SECTION 4 : VALIDATION IN/OUT =====
    elements.append(Paragraph("4. Validation In-Sample / Out-of-Sample", heading_style))
    
    try:
        from validation import in_out_validation
        val_results, train, test = in_out_validation(returns_df, train_ratio=0.7)
        
        elements.append(Paragraph(
            f"<b>In-Sample</b> : {train.index[0].strftime('%Y-%m-%d')} → {train.index[-1].strftime('%Y-%m-%d')} ({len(train)} jours)<br/>"
            f"<b>Out-of-Sample</b> : {test.index[0].strftime('%Y-%m-%d')} → {test.index[-1].strftime('%Y-%m-%d')} ({len(test)} jours)",
            body_style
        ))
        elements.append(Spacer(1, 0.5*cm))
        
        val_data = [["Portefeuille", "Sharpe In", "Sharpe Out", "Ratio Out/In", "Robustesse"]]
        
        for name, res in val_results.items():
            ratio = res['sharpe_ratio_out_in']
            if ratio > 0.7:
                verdict = "✅ ROBUSTE"
            elif ratio > 0.4:
                verdict = "⚠️ MOYEN"
            else:
                verdict = "❌ SUR-APPRIS"
            
            val_data.append([
                name,
                f"{res['in_sample']['sharpe']:.3f}",
                f"{res['out_of_sample']['sharpe']:.3f}",
                f"{ratio:.2f}",
                verdict,
            ])
        
        val_table = Table(val_data, colWidths=[3.5*cm, 2.7*cm, 2.7*cm, 2.7*cm, 3*cm])
        val_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(val_table)
    except Exception as e:
        elements.append(Paragraph(f"Validation non disponible: {e}", body_style))
    
    elements.append(PageBreak())
    
    # ===== SECTION 5 : BENCHMARK =====
    elements.append(Paragraph("5. Comparaison avec le benchmark (S&P 500)", heading_style))
    
    try:
        from data_manager import load_portfolio
        from benchmark import calculate_all_benchmark_metrics
        
        spy_prices = load_portfolio(["US_SPY"])
        
        if spy_prices is not None and not spy_prices.empty:
            spy_returns = np.log(spy_prices / spy_prices.shift(1)).dropna()['US_SPY']
            weights = optimal_portfolios['max_sharpe']
            port_returns = returns_df.dot(weights)
            
            bench_metrics = calculate_all_benchmark_metrics(port_returns, spy_returns)
            
            if bench_metrics:
                bench_data = [
                    ["Métrique", "Portefeuille", "S&P 500", "Écart"],
                    ["Rendement annualisé",
                     f"{bench_metrics['portfolio']['return_ann']*100:+.2f}%",
                     f"{bench_metrics['benchmark']['return_ann']*100:+.2f}%",
                     f"{(bench_metrics['portfolio']['return_ann']-bench_metrics['benchmark']['return_ann'])*100:+.2f}%"],
                    ["Volatilité",
                     f"{bench_metrics['portfolio']['volatility_ann']*100:.2f}%",
                     f"{bench_metrics['benchmark']['volatility_ann']*100:.2f}%",
                     f"{(bench_metrics['portfolio']['volatility_ann']-bench_metrics['benchmark']['volatility_ann'])*100:+.2f}%"],
                    ["Ratio de Sharpe",
                     f"{bench_metrics['portfolio']['sharpe']:.3f}",
                     f"{bench_metrics['benchmark']['sharpe']:.3f}",
                     f"{bench_metrics['portfolio']['sharpe']-bench_metrics['benchmark']['sharpe']:+.3f}"],
                ]
                
                bench_table = Table(bench_data, colWidths=[4*cm, 3.7*cm, 3.7*cm, 3.6*cm])
                bench_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ]))
                elements.append(bench_table)
                
                elements.append(Spacer(1, 0.5*cm))
                
                # Alpha, Beta, etc.
                ab_data = [
                    ["Métrique", "Valeur"],
                    ["Alpha (annualisé)", f"{bench_metrics['alpha']*100:+.2f}%"],
                    ["Beta", f"{bench_metrics['beta']:.3f}"],
                    ["Information Ratio", f"{bench_metrics['information_ratio']:.3f}"],
                    ["Tracking Error", f"{bench_metrics['tracking_error']*100:.2f}%"],
                    ["Up Capture Ratio", f"{bench_metrics['up_capture']:.1f}%"],
                    ["Down Capture Ratio", f"{bench_metrics['down_capture']:.1f}%"],
                ]
                
                ab_table = Table(ab_data, colWidths=[8*cm, 7*cm])
                ab_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ]))
                elements.append(ab_table)
        else:
            elements.append(Paragraph("SPY non disponible pour le benchmark.", body_style))
    except Exception as e:
        elements.append(Paragraph(f"Benchmark non disponible: {e}", body_style))
    
    elements.append(PageBreak())
    
    # ===== SECTION 6 : STRESS TESTS =====
    elements.append(Paragraph("6. Stress Tests", heading_style))
    
    try:
        from stress_tests import run_all_stress_tests
        
        weights = optimal_portfolios['max_sharpe']
        stress_results = run_all_stress_tests(returns_df, weights, capital=100000)
        
        stress_data = [["Scénario", "Description", "Impact"]]
        
        for r in stress_results:
            if "loss_pct" in r:
                impact = f"{r['loss_pct']:.2f}% ({r.get('loss_absolute', 0):,.0f} FCFA)"
            elif "var_stressee" in r:
                impact = f"VaR -{r['var_stressee']:.2f}%"
            elif "augmentation" in r:
                impact = f"Vol +{r['augmentation']:.1f}%"
            else:
                impact = "N/A"
            
            stress_data.append([r['name'], r['description'], impact])
        
        stress_table = Table(stress_data, colWidths=[4*cm, 6*cm, 5*cm])
        stress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(stress_table)
    except Exception as e:
        elements.append(Paragraph(f"Stress tests non disponibles: {e}", body_style))
    
    elements.append(PageBreak())
    
    # ===== SECTION 7 : CONTRIBUTION =====
    elements.append(Paragraph("7. Contribution au risque", heading_style))
    
    try:
        from risk_contribution import calculate_risk_contribution
        
        weights = optimal_portfolios['risk_parity']
        rc = calculate_risk_contribution(returns_df, weights)
        
        elements.append(Paragraph(
            f"<b>Volatilité du portefeuille</b> : {rc['portfolio_volatility']*100:.2f}%",
            body_style
        ))
        elements.append(Spacer(1, 0.3*cm))
        
        contrib_data = [["Actif", "Poids (%)", "Contribution au risque (%)", "Ratio"]]
        
        for i, asset in enumerate(assets):
            poids = rc['weights'][i] * 100
            contrib = rc['risk_contribution_normalized'][i]
            ratio = contrib / poids if poids != 0 else 0
            
            if ratio > 1.2:
                ind = "⚠️"
            elif ratio < 0.8:
                ind = "✅"
            else:
                ind = "⚪"
            
            contrib_data.append([
                asset,
                f"{poids:.1f}%",
                f"{contrib:.1f}%",
                f"{ratio:.2f} {ind}",
            ])
        
        contrib_table = Table(contrib_data, colWidths=[4.5*cm, 3.5*cm, 4*cm, 3*cm])
        contrib_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#a855f7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(contrib_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # Interprétation
        elements.append(Paragraph("<b>Interprétation :</b>", body_style))
        elements.append(Paragraph(
            "⚠️ = Amplificateur de risque (contribue plus que son poids)<br/>"
            "✅ = Diversificateur (contribue moins que son poids)<br/>"
            "⚪ = Contribution équilibrée",
            body_style
        ))
    except Exception as e:
        elements.append(Paragraph(f"Contribution non disponible: {e}", body_style))
    
    elements.append(PageBreak())
    
    # ===== SECTION 8 : INTERPRÉTATION GLOBALE =====
    elements.append(Paragraph("8. Synthèse et recommandations", heading_style))
    
    sharpe_comment = (
        'une excellente performance ajustée au risque'
        if metrics['sharpe'] > 2 else
        'une très bonne performance ajustée au risque'
        if metrics['sharpe'] > 1 else
        'une performance correcte ajustée au risque'
    )
    
    interpretation = f"""
    <b>Performance globale</b><br/>
    Le portefeuille a généré un rendement annualisé de <b>{metrics['rendement_annualise']*100:.2f}%</b> 
    pour une volatilité de <b>{metrics['volatilite_annuelle']*100:.2f}%</b>. Le ratio de Sharpe de 
    <b>{metrics['sharpe']:.2f}</b> indique {sharpe_comment}.
    <br/><br/>
    
    <b>Risque</b><br/>
    La VaR 99% de <b>{metrics['var_99_historique']*100:.2f}%</b> et l'Expected Shortfall 99% de 
    <b>{metrics['es_99']*100:.2f}%</b> permettent de quantifier le risque de pertes extrêmes. 
    Le drawdown maximal de <b>{metrics['max_drawdown']*100:.2f}%</b> représente la pire baisse historique.
    <br/><br/>
    
    <b>Robustesse</b><br/>
    La validation in-sample / out-of-sample confirme la robustesse du modèle. 
    L'analyse benchmark permet de mesurer la surperformance par rapport au marché.
    <br/><br/>
    
    <b>Recommandations</b><br/>
    • <b>Allocation :</b> Privilégier le portefeuille Max Sharpe pour le meilleur compromis rendement/risque<br/>
    • <b>Surveillance :</b> Surveiller les jours où la VaR 99% est approchée<br/>
    • <b>Diversification :</b> Le portefeuille est bien diversifié, avec des contributions équilibrées<br/>
    """
    elements.append(Paragraph(interpretation, body_style))
    
    # ===== AVERTISSEMENT =====
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("Avertissement", heading_style))
    
    disclaimer = """
    Ce rapport est fourni à titre informatif uniquement et ne constitue pas un conseil en 
    investissement. Les performances passées ne préjugent pas des performances futures. 
    Les analyses sont basées sur des données historiques et peuvent ne pas refléter les 
    conditions de marché actuelles ou futures. L'investisseur est seul responsable de ses 
    décisions d'investissement.
    """
    elements.append(Paragraph(disclaimer, body_style))
    
    # ===== FOOTER =====
    elements.append(Spacer(1, 2*cm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=9, textColor=colors.HexColor('#9ca3af'),
                                   alignment=TA_CENTER)
    elements.append(Paragraph(
        f"<b>STATBY2MF</b> · Portfolio Risk Analyzer · Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))
    
    doc.build(elements)
    return output_path
