from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from apps.detection.models import DetectionResult
from .models import Report
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF
from io import BytesIO
from datetime import datetime


class NumberedCanvas(canvas.Canvas):
    """Custom canvas with header and footer"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Header - Blue gradient bar
        self.setFillColor(colors.HexColor('#4A90E2'))
        self.rect(0, A4[1] - 80, A4[0], 80, fill=True, stroke=False)

        # Header - White text
        self.setFillColor(colors.white)
        self.setFont('Helvetica-Bold', 24)
        self.drawString(60, A4[1] - 40, 'ORAL CANCER')
        self.drawString(60, A4[1] - 62, 'DETECTION REPORT')

        # Header - AI Badge
        self.setFillColor(colors.white)
        self.circle(A4[0] - 100, A4[1] - 50, 25, fill=True, stroke=False)
        self.setFillColor(colors.HexColor('#4A90E2'))
        self.setFont('Helvetica-Bold', 18)
        self.drawCentredString(A4[0] - 100, A4[1] - 57, 'AI')

        # Footer - Decorative line
        self.setStrokeColor(colors.HexColor('#4A90E2'))
        self.setLineWidth(2)
        self.line(60, 60, A4[0] - 60, 60)

        # Footer - Left: Date
        self.setFillColor(colors.HexColor('#6C757D'))
        self.setFont('Helvetica', 9)
        self.drawString(60, 40, f'Generated: {datetime.now().strftime("%B %d, %Y")}')

        # Footer - Center: Organization
        self.setFont('Helvetica-Bold', 9)
        self.drawCentredString(A4[0]/2, 40, 'OralCare AI Medical System')

        # Footer - Right: Page number
        self.setFont('Helvetica', 9)
        self.drawRightString(A4[0] - 60, 40, f'Page {self._pageNumber} of {page_count}')


@login_required
def generate(request, id):
    """Generate premium PDF report"""
    detection_result = get_object_or_404(DetectionResult, id=id, user=request.user)

    # Get all results for this image
    all_results = DetectionResult.objects.filter(
        image=detection_result.image,
        user=request.user
    ).order_by('-confidence_score')

    # Create report record
    report, created = Report.objects.get_or_create(
        detection_result=detection_result,
        user=request.user
    )

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=60,
        leftMargin=60,
        topMargin=100,
        bottomMargin=80
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#4A90E2'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.white,
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#4A90E2'),
        borderPadding=(10, 5, 10, 5)
    )

    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2C3E50'),
        leading=16
    )

    # ===== COVER PAGE =====
    elements.append(Spacer(1, 1*inch))

    # Main Title
    elements.append(Paragraph("MEDICAL ANALYSIS REPORT", title_style))
    elements.append(Paragraph("AI-Powered Oral Cancer Detection", subtitle_style))

    elements.append(Spacer(1, 0.5*inch))

    # Report Summary Box
    summary_data = [
        ['REPORT ID', str(report.id)[:13].upper()],
        ['GENERATION DATE', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
        ['MEDICAL PROFESSIONAL', request.user.get_full_name() or request.user.username],
        ['INSTITUTION', request.user.institution or 'Not Specified'],
        ['IMAGE FILENAME', detection_result.image.filename],
    ]

    summary_table = Table(summary_data, colWidths=[2.2*inch, 3.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#E0E0E0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)

    elements.append(Spacer(1, 0.8*inch))

    # Primary Prediction - Large Banner
    primary_result = all_results[0] if all_results else detection_result
    pred_color = colors.HexColor('#DC3545') if primary_result.prediction == 'Cancer' else colors.HexColor('#28A745')

    prediction_data = [[primary_result.prediction.upper()]]
    prediction_table = Table(prediction_data, colWidths=[5.7*inch])
    prediction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), pred_color),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 32),
        ('TOPPADDING', (0, 0), (0, 0), 25),
        ('BOTTOMPADDING', (0, 0), (0, 0), 25),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
    ]))
    elements.append(prediction_table)

    elements.append(Spacer(1, 0.3*inch))

    # Confidence Score Box
    confidence_text = f"{primary_result.confidence_percentage:.1f}% CONFIDENCE"
    conf_data = [[confidence_text]]
    conf_table = Table(conf_data, colWidths=[5.7*inch])
    conf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F8F9FA')),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 22),
        ('TOPPADDING', (0, 0), (0, 0), 15),
        ('BOTTOMPADDING', (0, 0), (0, 0), 15),
    ]))
    elements.append(conf_table)

    # Page Break
    elements.append(PageBreak())

    # ===== DETAILED ANALYSIS PAGE =====
    elements.append(Paragraph("  DETECTION ANALYSIS  ", section_header))
    elements.append(Spacer(1, 0.2*inch))

    # Model Results Table
    if len(all_results) > 1:
        model_data = [['MODEL', 'PREDICTION', 'CONFIDENCE', 'PROCESSING TIME']]
        for result in all_results:
            model_data.append([
                result.model_name,
                result.prediction,
                f"{result.confidence_percentage:.1f}%",
                f"{result.processing_time:.2f}s"
            ])

        model_table = Table(model_data, colWidths=[1.8*inch, 1.5*inch, 1.4*inch, 1.6*inch])
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        elements.append(model_table)
    else:
        # Single model result
        single_data = [
            ['Model Used', primary_result.model_name],
            ['Prediction', primary_result.prediction],
            ['Confidence Score', f"{primary_result.confidence_percentage:.1f}%"],
            ['Processing Time', f"{primary_result.processing_time:.2f} seconds"],
            ['Model Version', primary_result.model_version or 'v1.0'],
            ['Analysis Date', primary_result.created_at.strftime('%B %d, %Y at %I:%M %p')],
        ]

        single_table = Table(single_data, colWidths=[2.2*inch, 4.2*inch])
        single_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
        ]))
        elements.append(single_table)

    elements.append(Spacer(1, 0.4*inch))

    # Image Information
    elements.append(Paragraph("  IMAGE INFORMATION  ", section_header))
    elements.append(Spacer(1, 0.2*inch))

    image_data = [
        ['Filename', detection_result.image.filename],
        ['File Size', f"{detection_result.image.file_size / 1024:.1f} KB"],
        ['Upload Date', detection_result.image.upload_date.strftime('%B %d, %Y at %I:%M %p')],
        ['Image Status', detection_result.image.status.upper()],
    ]

    image_table = Table(image_data, colWidths=[2.2*inch, 4.2*inch])
    image_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
    ]))
    elements.append(image_table)

    # Medical Disclaimer
    elements.append(Spacer(1, 0.6*inch))

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6C757D'),
        alignment=TA_JUSTIFY,
        leading=14,
        borderPadding=15,
        borderColor=colors.HexColor('#FFC107'),
        borderWidth=2,
        backColor=colors.HexColor('#FFF3CD')
    )

    disclaimer_text = """
    <b>IMPORTANT MEDICAL DISCLAIMER:</b> This AI-powered detection system is designed for research and educational purposes only.
    The results provided are NOT a definitive medical diagnosis and should NOT be used as a substitute for professional medical advice,
    diagnosis, or treatment. Always consult with qualified healthcare professionals and licensed medical practitioners for accurate
    diagnosis and appropriate medical care. The AI model's predictions should be used only as a supplementary tool to assist medical professionals.
    """

    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    # Footer Note
    elements.append(Spacer(1, 0.4*inch))

    footer_style = ParagraphStyle(
        'FooterNote',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6C757D'),
        alignment=TA_CENTER,
        leading=12
    )

    footer_text = """
    <b>Powered by Advanced Deep Learning Models</b><br/>
    RegNetY320 Architecture (89.4% Accuracy) | VGG16 Architecture (73.7% Accuracy)<br/>
    OralCare AI - Medical Detection System | Saveetha University
    """

    elements.append(Paragraph(footer_text, footer_style))

    # Build PDF with custom canvas
    doc.build(elements, canvasmaker=NumberedCanvas)

    # Get PDF value
    pdf = buffer.getvalue()
    buffer.close()

    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    filename = f'OralCancer_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)

    messages.success(request, 'Premium PDF Report generated successfully!')
    return response


@login_required
def download(request, id):
    """Download existing PDF report"""
    report = get_object_or_404(Report, id=id, user=request.user)
    return redirect('reports:generate', id=report.detection_result.id)
