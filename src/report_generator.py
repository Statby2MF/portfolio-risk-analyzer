"""
Génération de rapport PDF professionnel
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
    Génère un rapport PDF professionnel
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
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    elements = []
    
    # ===== PAGE DE GARDE =====
    elements.append(Spacer(1, 3*cm))
    elements.append(Paragraph("📊 Portfolio Risk Analyzer", title_style))
    elements.append(Paragraph(
        "Rapport d'analyse des risques",
        subtitle_style
    ))
    elements.append(Spacer(1, 2*cm))
    
    # Informations générales
    info_data = [
        ["Portefeuille", portfolio_name],
        ["Actifs analysés", ", ".join(assets)],
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
    
    # ===== SECTION 1 : MÉTRIQUES DE PERFORMANCE =====
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(perf_table)
    
    # ===== SECTION 2 : MÉTRIQUES DE RISQUE =====
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
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(risk_table)
    
    elements.append(PageBreak())
    
    # ===== SECTION 3 : ALLOCATION OPTIMALE =====
    elements.append(Paragraph("3. Allocation optimale (Markowitz)", heading_style))
    
    elements.append(Paragraph(
        "Les allocations ci-dessous sont calculées selon trois approches : "
        "maximisation du ratio de Sharpe, minimisation de la volatilité, "
        "et Risk Parity (contribution égale au risque).",
        body_style
    ))
    
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(alloc_table)
    
   interpretation = f"""
<b>Performance du portefeuille</b><br/>
Sur la période analysée, le portefeuille a généré un rendement annualisé de 
<b>{metrics['rendement_annualise']*100:.2f}%</b> pour une volatilité de 
<b>{metrics['volatilite_annuelle']*100:.2f}%</b>. Le ratio de Sharpe de 
<b>{metrics['sharpe']:.2f}</b> indique {(
    'une excellente performance ajustée au risque, largement supérieure au marché'
    if metrics['sharpe'] > 2 else
    'une très bonne performance ajustée au risque'
    if metrics['sharpe'] > 1 else
    'une performance correcte ajustée au risque'
    if metrics['sharpe'] > 0.5 else
    'une performance faible ajustée au risque, à améliorer'
)}. Le ratio de Sortino de <b>{metrics['sortino']:.2f}</b> confirme que la performance 
est {'très solide' if metrics['sortino'] > 1.5 else 'correcte'} lorsque l'on ne pénalise 
que la volatilité à la baisse.
<br/><br/>

<b>Analyse du risque</b><br/>
La VaR à 99% de <b>{metrics['var_99_historique']*100:.2f}%</b> signifie que dans 99% des cas, 
la perte journalière ne devrait pas dépasser ce seuil. Autrement dit, sur 100 jours de trading, 
seul 1 jour pourrait enregistrer une perte supérieure à ce niveau. 
L'Expected Shortfall de <b>{metrics['es_99']*100:.2f}%</b> — qui mesure la perte moyenne 
lorsque ce seuil est franchi — reste {'contenu' if abs(metrics['es_99']) < 0.05 else 'élevé'}, 
ce qui indique {'une bonne résistance aux chocs extrêmes' if abs(metrics['es_99']) < 0.05 else 'une vulnérabilité aux événements de marché exceptionnels'}.
<br/><br/>

<b>Résistance aux crises</b><br/>
Le drawdown maximal de <b>{metrics['max_drawdown']*100:.2f}%</b> représente la pire baisse 
enregistrée sur la période. Un drawdown {'faible' if abs(metrics['max_drawdown']) < 0.1 else 'modéré' if abs(metrics['max_drawdown']) < 0.2 else 'important'} 
signifie que le portefeuille {'a bien résisté aux phases de correction' if abs(metrics['max_drawdown']) < 0.1 else 'a connu des phases de stress notables'}. 
Le ratio de Calmar de <b>{metrics['rendement_annualise'] / abs(metrics['max_drawdown']):.2f}</b> 
(rendement / drawdown) confirme {'une bonne efficacité' if metrics['rendement_annualise'] / abs(metrics['max_drawdown']) > 1 else 'une efficacité limitée'} 
dans la gestion des phases baissières.
<br/><br/>

<b>Forme de la distribution</b><br/>
La skewness de <b>{metrics['skewness']:.3f}</b> indique une distribution {(
    'légèrement asymétrique à droite (plus de gains extrêmes que de pertes)'
    if metrics['skewness'] > 0.1 else
    'légèrement asymétrique à gauche (plus de pertes extrêmes que de gains)'
    if metrics['skewness'] < -0.1 else
    'quasi-symétrique'
)}. La kurtosis de <b>{metrics['kurtosis']:.3f}</b> ({(
    'queues épaisses — risque d\\'événements extrêmes plus fréquents que sous une loi normale'
    if metrics['kurtosis'] > 1 else
    'proche de la loi normale'
    if abs(metrics['kurtosis']) < 0.5 else
    'queues légèrement plus fines que la normale'
)}).
<br/><br/>

<b>Recommandations</b><br/>
• <b>Allocation suggérée :</b> Privilégier le portefeuille Max Sharpe qui offre le meilleur 
compromis rendement/risque.<br/>
• <b>Surveillance :</b> Porter une attention particulière aux jours où la perte approche 
la VaR 99% ({metrics['var_99_historique']*100:.2f}%).<br/>
• <b>Diversification :</b> {(
    'Le portefeuille est bien diversifié avec des contributions de risque équilibrées.'
    if metrics['sharpe'] > 1 else
    'Envisager une diversification accrue pour réduire la volatilité.'
)}<br/>
"""
    
    # ===== SECTION 5 : AVERTISSEMENT =====
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("5. Avertissement", heading_style))
    
    disclaimer = """
    Ce rapport est fourni à titre informatif uniquement et ne constitue pas un conseil 
    en investissement. Les performances passées ne préjugent pas des performances futures. 
    Les analyses sont basées sur des données historiques et peuvent ne pas refléter les 
    conditions de marché actuelles ou futures. L'investisseur est seul responsable de ses 
    décisions d'investissement.
    """
    elements.append(Paragraph(disclaimer, body_style))
    
    # ===== FOOTER =====
    elements.append(Spacer(1, 2*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Portfolio Risk Analyzer · Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))
    
    # Génération
    doc.build(elements)
    return output_path
