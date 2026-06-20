"""
Aayu AI — PDF Report Generator
Uses ReportLab to generate clean, color-coded PDF reports.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io


# Colors matching the app theme
COLORS = {
    'teal': HexColor('#0D9488'),
    'red': HexColor('#EF4444'),
    'blue': HexColor('#3B82F6'),
    'green': HexColor('#10B981'),
    'amber': HexColor('#F59E0B'),
    'dark': HexColor('#0F172A'),
    'grey': HexColor('#64748B'),
    'light_grey': HexColor('#F1F5F9'),
    'white': HexColor('#FFFFFF'),
}

STATUS_COLORS = {
    'NORMAL': COLORS['green'],
    'HIGH': COLORS['red'],
    'LOW': COLORS['blue'],
    'CRITICAL': COLORS['red'],
}


def generate_pdf_report(report_data, parameters, health_score):
    """Generate a PDF report with color-coded results.
    
    Args:
        report_data: Dict with patient info, date, lab name.
        parameters: List of parameter dicts.
        health_score: Dict with overall score and sub-scores.
    
    Returns:
        bytes: PDF file content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm,
                            leftMargin=15*mm, rightMargin=15*mm)

    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=24, textColor=COLORS['teal'],
                                  spaceAfter=6*mm)
    story.append(Paragraph('Aayu AI — Health Report', title_style))

    # Patient info
    info_style = ParagraphStyle('Info', parent=styles['Normal'],
                                 fontSize=11, textColor=COLORS['grey'])
    patient = report_data.get('patient_name', 'Patient')
    date = report_data.get('test_date', 'N/A')
    lab = report_data.get('lab_name', 'N/A')
    story.append(Paragraph(f'{patient} · {date} · {lab}', info_style))
    story.append(Spacer(1, 8*mm))

    # Health Score
    score_style = ParagraphStyle('Score', parent=styles['Normal'],
                                  fontSize=16, textColor=COLORS['dark'])
    score_val = health_score.get('overall', 0)
    score_color = COLORS['green'] if score_val >= 70 else COLORS['amber'] if score_val >= 50 else COLORS['red']
    story.append(Paragraph(f'Health Score: <font color="{score_color}">{score_val}/100</font>', score_style))
    story.append(Spacer(1, 6*mm))

    # Parameters table
    table_data = [['Test', 'Value', 'Unit', 'Normal Range', 'Status']]
    for p in parameters:
        ref = f"{p.get('ref_low', '-')} – {p.get('ref_high', '-')}"
        table_data.append([
            p['test'],
            str(p['value']),
            p['unit'],
            ref,
            p.get('status', 'NORMAL')
        ])

    table = Table(table_data, colWidths=[45*mm, 25*mm, 20*mm, 35*mm, 25*mm])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['teal']),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['light_grey']),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], COLORS['light_grey']]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])

    # Color-code abnormal rows
    for i, p in enumerate(parameters, start=1):
        status = p.get('status', 'NORMAL')
        if status in ('HIGH', 'CRITICAL'):
            table_style.add('TEXTCOLOR', (4, i), (4, i), COLORS['red'])
        elif status == 'LOW':
            table_style.add('TEXTCOLOR', (4, i), (4, i), COLORS['blue'])
        else:
            table_style.add('TEXTCOLOR', (4, i), (4, i), COLORS['green'])

    table.setStyle(table_style)
    story.append(table)

    # Disclaimer
    story.append(Spacer(1, 10*mm))
    disc_style = ParagraphStyle('Disclaimer', parent=styles['Normal'],
                                 fontSize=8, textColor=COLORS['grey'])
    story.append(Paragraph(
        '⚕️ Disclaimer: Aayu AI provides educational health insights only. '
        'Not a substitute for professional medical advice.', disc_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
