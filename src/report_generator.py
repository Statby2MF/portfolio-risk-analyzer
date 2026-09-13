"""
Génération de rapport PDF professionnel - Version condensée
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
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                  fontSize=22, textColor=colors.HexColor('#c9a227'),
                                  spaceAfter=15, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#6b7280'),
                                     spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                    fontSize=14, textColor=colors.HexColor('#0a3d2e'),
                                    spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'],
                                 fontSize=10, textColor=colors.HexColor('#374151'),
                                 alignment=TA_JUSTIFY, spaceAfter=8)
    
    elements = []
    
    # ===== PAGE DE GARDE =====
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("📊 Portfolio Risk Analyzer", title_style))
    elements.append(Paragraph("Rapport d'analyse des risques", subtitle_style))
    elements.append(Spacer(1, 1*cm))
    
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
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(info_table)
    elements.append(PageBreak())
    
    # ===== SECTION 1 : PERFORMANCE + RISQUE (combinés) =====
    elements.append(Paragraph("1. Métriques de performance et de risque", heading_style))
    
    perf_data = [
        ["Performance", "", "Risque", ""],
        ["Rendement annualisé", f"{metrics['rendement_annualise']*100:.2f}%",
         "VaR 95%", f"{metrics['var_95_historique']*100:.2f}%"],
        ["Volatilité annualisée", f"{metrics['volatilite_annuelle']*100:.2f}%",
         "VaR 99%", f"{metrics['var_99_historique']*100:.2f}%"],
        ["Ratio de Sharpe", f"{metrics['sharpe']:.2f}",
         "ES 95%", f"{metrics['es_95']*100:.2f}%"],
        ["Ratio de Sortino", f"{metrics['sortino']:.2f}",
         "ES 99%", f"{metrics['es_99']*100:.2f}%"],
        ["", "", "Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%"],
        ["", "", "Skewness / Kurtosis", f"{metrics['skewness']:.3f} / {metrics['kurtosis']:.3f}"],
    ]
    
    perf_table = Table(perf_data, colWidths=[4.5*cm, 3*cm, 4.5*cm, 3.5*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c9a227')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    elements.append(perf_table)
    
    # ===== SECTION 2 : ALLOCATION =====
    elements.append(Paragraph("2. Allocation optimale (Markowitz)", heading_style))
    
    alloc_data = [["Actif", "Max Sharpe", "Min Volatilité", "Risk Parity"]]
    for i, asset in enumerate(assets):
        alloc_data.append([
            asset,
            f"{optimal_portfolios['max_sharpe'][i]*100:.1f}%",
            f"{optimal_portfolios['min_volatility'][i]*100:.1f}%",
            f"{optimal_portfolios['risk_parity'][i]*100:.1f}%",
        ])
    
    alloc_table = Table(alloc_data, colWidths=[4.5*cm, 3.6*cm, 3.6*cm, 3.6*cm])
    alloc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a3d2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(alloc_table)
    
    # ===== SECTION 3 : VALIDATION =====
    elements.append(Paragraph("3. Validation In-Sample / Out-of-Sample", heading_style))
    
    try:
        from validation import in_out_validation
        val_results, train, test = in_out_validation(returns_df, train_ratio=0.7)
        
        elements.append(Paragraph(
            f"<b>In-Sample</b> : {train.index[0].strftime('%Y-%m-%d')} → {train.index[-1].strftime('%Y-%m-%d')} ({len(train)} jours) | "
            f"<b>Out-of-Sample</b> : {test.index[0].strftime('%Y-%m-%d')} → {test.index[-1].strftime('%Y-%m-%d')} ({len(test)} jours)",
            body_style
        ))
        
        val_data = [["Portefeuille", "Sharpe In", "Sharpe Out", "Ratio", "Robustesse"]]
        for name, res in val_results.items():
            ratio = res['sharpe_ratio_out_in']
            verdict = "ROBUSTE" if ratio > 0.7 else "MOYEN" if ratio > 0.4 else "SUR-APPRIS"
            val_data.append([
                name,
                f"{res['in_sample']['sharpe']:.3f}",
                f"{res['out_of_sample']['sharpe']:.3f}",
                f"{ratio:.2f}",
                verdict,
            ])
        
        val_table = Table(val_data, colWidths=[3.5*cm, 2.8*cm, 2.8*cm, 2.5*cm, 3.5*cm])
        val_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(val_table)
    except Exception as e:
        elements.append(Paragraph(f"Validation non disponible: {e}", body_style))
    
    # ===== SECTION 4 : BENCHMARK =====
    elements.append(Paragraph("4. Comparaison avec le benchmark (S&P 500)", heading_style))
    
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
                    ["Sharpe",
                     f"{bench_metrics['portfolio']['sharpe']:.3f}",
                     f"{bench_metrics['benchmark']['sharpe']:.3f}",
                     f"{bench_metrics['portfolio']['sharpe']-bench_metrics['benchmark']['sharpe']:+.3f}"],
                    ["Alpha / Beta",
                     f"{bench_metrics['alpha']*100:+.2f}%",
                     f"{bench_metrics['beta']:.3f}",
                     f"Info Ratio: {bench_metrics['information_ratio']:.3f}"],
                ]
                
                bench_table = Table(bench_data, colWidths=[4*cm, 3.7*cm, 3.7*cm, 3.7*cm])
                bench_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ]))
                elements.append(bench_table)
    except Exception as e:
        elements.append(Paragraph(f"Benchmark non disponible: {e}", body_style))
    
    # ===== SECTION 5 : STRESS TESTS =====
    elements.append(Paragraph("5. Stress Tests", heading_style))
    
    try:
        from stress_tests import run_all_stress_tests
        
        weights = optimal_portfolios['max_sharpe']
        stress_results = run_all_stress_tests(returns_df, weights, capital=100000)
        
        stress_data = [["Scénario", "Impact"]]
        for r in stress_results:
            if "loss_pct" in r:
                impact = f"{r['loss_pct']:.2f}% ({r.get('loss_absolute', 0):,.0f} FCFA)"
            elif "var_stressee" in r:
                impact = f"VaR -{r['var_stressee']:.2f}%"
            elif "augmentation" in r:
                impact = f"Vol +{r['augmentation']:.1f}%"
            else:
                impact = "N/A"
            stress_data.append([r['name'], impact])
        
        stress_table = Table(stress_data, colWidths=[7*cm, 8*cm])
        stress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(stress_table)
    except Exception as e:
        elements.append(Paragraph(f"Stress tests non disponibles: {e}", body_style))
    
    # ===== SECTION 6 : CONTRIBUTION =====
    elements.append(Paragraph("6. Contribution au risque (Risk Parity)", heading_style))
    
    try:
        from risk_contribution import calculate_risk_contribution
        
        weights = optimal_portfolios['risk_parity']
        rc = calculate_risk_contribution(returns_df, weights)
        
        contrib_data = [["Actif", "Poids", "Contribution", "Ratio"]]
        for i, asset in enumerate(assets):
            poids = rc['weights'][i] * 100
            contrib = rc['risk_contribution_normalized'][i]
            ratio = contrib / poids if poids != 0 else 0
            ind = "⚠️" if ratio > 1.2 else "✅" if ratio < 0.8 else "⚪"
            
            contrib_data.append([
                asset, f"{poids:.1f}%", f"{contrib:.1f}%", f"{ratio:.2f} {ind}"
            ])
        
        contrib_table = Table(contrib_data, colWidths=[4.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        contrib_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#a855f7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(contrib_table)
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(
            "⚠️ Amplificateur de risque · ✅ Diversificateur · ⚪ Équilibré",
            body_style
        ))
    except Exception as e:
        elements.append(Paragraph(f"Contribution non disponible: {e}", body_style))
    
    # ===== SECTION 7 : SYNTHÈSE =====
    elements.append(Paragraph("7. Synthèse et recommandations", heading_style))
    
    sharpe_comment = (
        'une excellente performance ajustée au risque' if metrics['sharpe'] > 2 else
        'une très bonne performance ajustée au risque' if metrics['sharpe'] > 1 else
        'une performance correcte ajustée au risque'
    )
    
    interpretation = f"""
    Le portefeuille a généré un rendement annualisé de <b>{metrics['rendement_annualise']*100:.2f}%</b> 
    pour une volatilité de <b>{metrics['volatilite_annuelle']*100:.2f}%</b>. Le ratio de Sharpe de 
    <b>{metrics['sharpe']:.2f}</b> indique {sharpe_comment}. La VaR 99% de 
    <b>{metrics['var_99_historique']*100:.2f}%</b> et l'ES 99% de <b>{metrics['es_99']*100:.2f}%</b> 
    quantifient le risque de pertes extrêmes. Le drawdown maximal de <b>{metrics['max_drawdown']*100:.2f}%</b> 
    représente la pire baisse historique.<br/><br/>
    <b>Recommandations :</b><br/>
    • Privilégier l'allocation Max Sharpe pour le meilleur compromis rendement/risque<br/>
    • Surveiller les jours où la VaR 99% est approchée<br/>
    • Le portefeuille est bien diversifié avec des contributions équilibrées
    """
    elements.append(Paragraph(interpretation, body_style))
    
    # ===== AVERTISSEMENT =====
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Avertissement", heading_style))
    elements.append(Paragraph(
        "Ce rapport est fourni à titre informatif uniquement et ne constitue pas un conseil en "
        "investissement. Les performances passées ne préjugent pas des performances futures.",
        body_style
    ))
    
    # ===== FOOTER =====
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=9, textColor=colors.HexColor('#9ca3af'),
                                   alignment=TA_CENTER)
    elements.append(Paragraph(
        f"<b>STATBY2MF</b> · Portfolio Risk Analyzer · {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))
    
    doc.build(elements)
    return output_path
