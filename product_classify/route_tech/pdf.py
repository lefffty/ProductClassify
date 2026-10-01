import os
from io import BytesIO
from typing import List

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

from route_tech.constants import TechRoutePdfConsts


_styles = getSampleStyleSheet()

class PdfGenerator:
    @staticmethod
    def _register_cyrillic_font() -> str:
        """Регистрирует шрифт с поддержкой кириллицы. Возвращает имя шрифта."""
        font_name = TechRoutePdfConsts.FONT_NAME
        font_path = os.path.join(
            settings.STATICFILES_DIRS[0],
            *TechRoutePdfConsts.FONT_PATH_PARTS,
        )
        pdfmetrics.registerFont(TTFont(font_name, font_path, "UTF-8"))
        return font_name

    @staticmethod
    def _make_styles(font_name: str):
        """Создаёт стили с указанием кириллического шрифта."""
        normal = ParagraphStyle(
            "TechRouteNormal",
            parent=_styles["Normal"],
            fontName=font_name,
            fontSize=TechRoutePdfConsts.NORMAL_FONTSIZE,
            leading=TechRoutePdfConsts.NORMAL_LEADING,
        )

        header = ParagraphStyle(
            "TechRouteHeader",
            parent=normal,
            fontName=font_name,
            fontSize=TechRoutePdfConsts.HEADER_FONTSIZE,
            textColor=colors.white,
            alignment=TechRoutePdfConsts.HEADER_ALIGNMENT,
        )

        title = ParagraphStyle(
            "TechRouteTitle",
            parent=_styles["Heading1"],
            fontName=font_name,
            fontSize=TechRoutePdfConsts.TITLE_FONTSIZE,
            alignment=TechRoutePdfConsts.TITLE_ALIGNMENT,
            spaceAfter=TechRoutePdfConsts.TITLE_SPACEAFTER,
        )

        return normal, header, title

    @staticmethod
    def _to_paragraph(value, style) -> Paragraph:
        """Оборачивает значение в Paragraph с кириллическим шрифтом.
        """
        if value is None or value == "":
            value = "—"
        return Paragraph(str(value), style)

    @staticmethod
    def create_tech_route_pdf(records: List["TechRouteRecord"], product) -> BytesIO:
        """Генерирует PDF с технологическим маршрутом изделия.

        :param records: список TechRouteRecord из TechRouteSelector
        :param product: объект Prod
        :return: BytesIO с готовым PDF (курсор в начале)
        """
        font_name = PdfGenerator._register_cyrillic_font()
        normal_style, header_style, title_style = PdfGenerator._make_styles(font_name)

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=TechRoutePdfConsts.LEFT_MARGIN,
            rightMargin=TechRoutePdfConsts.RIGHT_MARGIN,
            topMargin=TechRoutePdfConsts.TOP_MARGIN,
            bottomMargin=TechRoutePdfConsts.BOTTOM_MARGIN,
        )

        # Заголовки колонок — многострочные, через <br/>
        headers = [
            "№",
            "Входное<br/>изделие",
            "Выходное<br/>изделие",
            "Операция",
            "Профессия",
            "Рабочий<br/>центр",
            "СЭД",
            "Квалификация",
            "Кол-во<br/>вход.",
            "Кол-во<br/>выход.",
            "T&nbsp;пз",
            "T&nbsp;шт",
            "Исп.",
        ]
        story = [[Paragraph(h, header_style) for h in headers]]

        # Строки данных — все текстовые ячейки через Paragraph
        for idx, r in enumerate(records, start=1):
            story.append([
                Paragraph(str(idx), normal_style),
                PdfGenerator._to_paragraph(r.input_prod_name, normal_style),
                PdfGenerator._to_paragraph(r.output_prod_name, normal_style),
                PdfGenerator._to_paragraph(r.operation_name, normal_style),
                PdfGenerator._to_paragraph(r.profession_name, normal_style),
                PdfGenerator._to_paragraph(r.gwc_name, normal_style),
                PdfGenerator._to_paragraph(r.eas_name, normal_style),
                PdfGenerator._to_paragraph(r.qualification_name, normal_style),
                PdfGenerator._to_paragraph(r.input_quantity, normal_style),
                PdfGenerator._to_paragraph(r.output_quantity, normal_style),
                PdfGenerator._to_paragraph(r.t_pz, normal_style),
                PdfGenerator._to_paragraph(r.t_sht, normal_style),
                PdfGenerator._to_paragraph(r.num_of_workers, normal_style),
            ])

        # Ширины колонок подобраны под landscape A4 (~842pt − 40pt отступов = ~802pt)
        col_widths = [24, 70, 70, 70, 70, 60, 70, 70, 50, 50, 40, 40, 30]

        table = Table(story, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Шапка
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(TechRoutePdfConsts.HEADER_BG)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

            # Тело
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), TechRoutePdfConsts.CELL_PADDING),
            ("RIGHTPADDING", (0, 0), (-1, -1), TechRoutePdfConsts.CELL_PADDING),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),

            # Выравнивание по колонкам
            ("ALIGN", (0, 1), (0, -1), "CENTER"),       # №
            ("ALIGN", (8, 1), (11, -1), "RIGHT"),       # числовые колонки
            ("ALIGN", (12, 1), (12, -1), "CENTER"),     # Исп.

            # Чередование фона строк
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor(TechRoutePdfConsts.ROW_BG_ALT)]),
        ]))

        elements = [
            Paragraph(f'Технологический маршрут изделия «{product.name}»', title_style),
            table,
            Spacer(*TechRoutePdfConsts.SPACER),
            Paragraph(
                f"Всего операций: {len(records)}.",
                normal_style,
            ),
        ]

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_tech_route_filename(product_name: str):
        return f"{product_name}_technological_route.pdf"
