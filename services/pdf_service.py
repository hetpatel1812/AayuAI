import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_report_pdf(report, parameters):
    """
    Generates a professional medical PDF summary of the AI analysis.
    Returns a BytesIO object containing the PDF data.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        textColor=colors.HexColor("#0B1437")
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor("#00B8A9")
    )
    
    normal_style = styles['Normal']
    
    elements = []
    
    # 1. Header
    elements.append(Paragraph("Aayu AI - Medical Report Analysis", title_style))
    
    # Patient Info Table
    patient_data = [
        ["Patient Name:", report.patient_name or "Unknown", "Test Date:", report.test_date or "Unknown"],
        ["Age/Gender:", f"{report.patient_age or '--'} / {report.patient_gender or '--'}", "Lab Name:", report.lab_name or "Unknown Lab"],
        ["AI Health Score:", f"{report.health_score}/100", "", ""]
    ]
    
    t_patient = Table(patient_data, colWidths=[100, 150, 100, 150])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1E293B")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(t_patient)
    elements.append(Spacer(1, 20))
    
    # 2. Abnormal Parameters (The most important part)
    elements.append(Paragraph("Key Findings (Requires Attention)", h2_style))
    
    abnormal_params = [p for p in parameters if p.status and p.status != 'NORMAL']
    
    if not abnormal_params:
        elements.append(Paragraph("All tested parameters are within normal ranges. Great job!", normal_style))
    else:
        for p in abnormal_params:
            # Param Header
            status_color = colors.red if p.status == 'HIGH' else colors.orange
            
            elements.append(Paragraph(f"<b>{p.test_name}</b> - {p.status}", ParagraphStyle(
                'ParamTitle', parent=styles['Normal'], fontSize=12, spaceAfter=5, textColor=status_color
            )))
            
            # Param Data
            val_str = f"<b>Value:</b> {p.value} {p.unit} (Normal: {p.ref_low} - {p.ref_high} {p.unit})"
            elements.append(Paragraph(val_str, normal_style))
            
            # AI Explanation
            if p.explanation:
                elements.append(Paragraph(f"<b>Explanation:</b> {p.explanation}", normal_style))
            if p.diet_tip:
                elements.append(Paragraph(f"<b>Recommendation:</b> {p.diet_tip}", normal_style))
                
            elements.append(Spacer(1, 15))

    # 3. All Parameters Table
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Complete Parameter List", h2_style))
    
    table_data = [["Test Name", "Value", "Unit", "Reference Range", "Status"]]
    for p in parameters:
        table_data.append([
            p.test_name, 
            str(p.value), 
            p.unit, 
            f"{p.ref_low} - {p.ref_high}", 
            p.status
        ])
        
    t_all = Table(table_data, repeatRows=1)
    t_all.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E2D5A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(t_all)
    
    # Build Document
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
