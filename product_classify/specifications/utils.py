import os

from django.conf import settings

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from io import BytesIO
from datetime import datetime
from typing import List

from products.models import Prod

from specifications.constants import TotalCostRatioConsts, ChangeLogConsts
from specifications.models import TotalCostRatioResult, SpecificationLogResult


styles = getSampleStyleSheet()

def to_string(text: str):
    return f'<font name="DejaVuSerif">{text}</font>'


def to_paragraph(text, style=styles['Normal']):
    return Paragraph(to_string(text), style)


def create_total_cost_ratio_pdf(results: List[TotalCostRatioResult], product: Prod):
    font_path = os.path.join(
        settings.STATICFILES_DIRS[0], 'fonts/DejaVuSerif.ttf')

    pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path, 'UTF-8'))

    font_name = 'DejaVuSerif'

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=TotalCostRatioConsts.RIGHT_MARGIN,
        leftMargin=TotalCostRatioConsts.LEFT_MARGIN,
        topMargin=TotalCostRatioConsts.TOP_MARGIN,
        bottomMargin=TotalCostRatioConsts.BOTTOM_MARGIN,
    )

    normal_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=TotalCostRatioConsts.NORMAL_FONTSIZE,
        leading=TotalCostRatioConsts.NORMAL_LEADING,
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=normal_style,
        fontName=font_name,
        fontSize=TotalCostRatioConsts.HEADER_FONTSIZE,
        textColor=colors.white,
        alignment=TotalCostRatioConsts.HEADER_ALIGNMENT,  # center
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=TotalCostRatioConsts.TITLE_FONTSIZE,
        alignment=TotalCostRatioConsts.TITLE_ALIGNMENT,
        spaceAfter=TotalCostRatioConsts.TITLE_SPACEAFTER
    )

    story = []

    total_cost = sum(item[6] for item in results)

    for result in results:
        processed_row = list(result)

        for i, _ in enumerate(processed_row):
            if i in (1, 3, 5):
                processed_row[i] = to_paragraph(processed_row[i])

        story.append(processed_row)

    story.insert(
        0,
        [
            Paragraph('ID родительского<br/>изделия', header_style),
            Paragraph('Название родительского<br/>изделия', header_style),
            Paragraph('ID дочернего<br/>изделия', header_style),
            Paragraph('Название дочернего<br/>изделия', header_style),
            Paragraph('Количество', header_style),
            Paragraph('Ед. изм.', header_style),
            Paragraph('Цена за<br/>N экземпляров', header_style),
            Paragraph('Уровень<br/>в дереве', header_style)
        ],
    )

    table = Table(story, colWidths=TotalCostRatioConsts.COL_WIDTHS, repeatRows=1)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),

        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'LEFT'),
        ('ALIGN', (5, 1), (6, -1), 'CENTER'),
        ('ALIGN', (7, 1), (7, -1), 'RIGHT'),
        ('ALIGN', (8, 1), (8, -1), 'CENTER'),

        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f8f9fa')]),

        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        ('FONTNAME', (0, 0), (-1, 0), font_name +
         '-Bold' if font_name == 'DejaVuSans' else 'Times-Bold'),
    ]))

    elements = []

    elements.append(
        Paragraph(f'СПЕЦИФИКАЦИЯ ИЗДЕЛИЯ "{product.name}"', title_style))

    elements.append(table)

    elements.append(Spacer(*TotalCostRatioConsts.SPACER))

    elements.append(
        Paragraph(
            f'Общая стоимость изделия: {total_cost:.5f} рублей.', style=normal_style)
    )

    elements.append(Spacer(*TotalCostRatioConsts.SPACER))

    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=normal_style,
        fontSize=TotalCostRatioConsts.SIGNATURE_FONTSIZE,
        spaceBefore=TotalCostRatioConsts.SIGNATURE_SPACEBEFORE
    )

    signatures = [
        Paragraph('Разработчик: ___________________', signature_style),
        Paragraph('Проверил: ___________________', signature_style),
        Paragraph('Утвердил: ___________________', signature_style),
    ]

    signature_table_data = [
        [signatures[0], signatures[1], signatures[2]]
    ]
    signature_table = Table(signature_table_data, colWidths=TotalCostRatioConsts.SIGNATURE_COL_WIDTHS)
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(signature_table)

    doc.build(elements)
    buffer.seek(0)

    return buffer


def create_change_log_pdf(results: List[SpecificationLogResult]) -> BytesIO:
    font_name = 'DejaVuSerif'

    font_path = os.path.join(
        settings.STATICFILES_DIRS[0], 'fonts/DejaVuSerif.ttf')

    pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path, 'UTF-8'))

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=ChangeLogConsts.LEFT_MARGIN,
        leftMargin=ChangeLogConsts.LEFT_MARGIN,
        topMargin=ChangeLogConsts.TOP_MARGIN,
        bottomMargin=ChangeLogConsts.BOTTOM_MARGIN
    )

    normal_style = ParagraphStyle(
        'NormalCyrillic',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=ChangeLogConsts.NORMAL_FONTSIZE,
        leading=ChangeLogConsts.NORMAL_LEADING,
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=ChangeLogConsts.TITLE_FONTSIZE,
        alignment=ChangeLogConsts.TITLE_ALIGNMENT,
        spaceAfter=ChangeLogConsts.TITLE_SPACEAFTER
    )

    table_header = [
        "Номер изменения",
        "ID родительского изделия",
        "ID дочернего изделия",
        "Дата внесения изменения",
        "Строковая запись изменения"
    ]

    story = []

    story.append([to_paragraph(h) for h in table_header])

    for result in results:
        processed_row = list(result)

        for i, value in enumerate(processed_row):
            if isinstance(value, str) and value.strip():
                processed_row[i] = to_paragraph(processed_row[i])

        story.append(processed_row)

    table = Table(story, colWidths=ChangeLogConsts.COL_WIDTHS)

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),

        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D3D3")),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor("#FFFFFF"), colors.HexColor("#F5F5F5")]),
    ])

    table.setStyle(table_style)

    elements = []

    title = Paragraph("Лог изменений", title_style)
    elements.append(title)

    elements.append(table)

    date_style = ParagraphStyle(
        'DateStyle',
        parent=normal_style,
        fontSize=ChangeLogConsts.DATE_FONTSIZE,
        textColor=colors.gray,
        alignment=ChangeLogConsts.DATE_ALIGNMENT
    )
    generation_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    date_text = Paragraph(f"Сгенерировано: {generation_date}", date_style)
    elements.append(Spacer(*ChangeLogConsts.SPACER))
    elements.append(date_text)

    doc.build(elements)

    buffer.seek(0)

    return buffer
