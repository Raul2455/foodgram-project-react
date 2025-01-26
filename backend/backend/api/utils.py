"""
Модуль для генерации PDF-файлов.

Этот модуль предоставляет функцию `generate_pdf`, которая создает PDF-файл
с использованием библиотеки ReportLab. Файл содержит текст, переданный
в качестве аргумента, и может быть использован для генерации списка покупок
или других документов.
"""

import os
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from django.http import HttpResponse
from django.conf import settings


def generate_shopping_list_pdf(text, filename="shopping_list.pdf"):
    """
    Генерирует PDF-файл на лету с использованием переданного текста.

    Args:
        text (str): Текст, который будет добавлен в PDF.
        filename (str): Имя файла для сохранения PDF.
        По умолчанию "shopping_list.pdf".

    Returns:
        HttpResponse: Ответ с PDF-файлом.
    """
    # Добавляем путь к шрифтам
    reportlab.rl_config.TTFSearchPath.append(
        os.path.join(settings.MEDIA_ROOT, 'fonts'))

    # Регистрируем шрифт
    pdfmetrics.registerFont(TTFont('Open Sans', 'opensans.ttf'))

    # Создаем стили для текста
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontName='Open Sans',
        fontSize=16,
        leading=20,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='ContentStyle',
        fontName='Open Sans',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_LEFT,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='FooterStyle',
        fontName='Open Sans',
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    ))

    # Создаем HTTP-ответ с PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Создаем PDF-документ
    pdf = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Содержимое PDF
    content = []

    # Добавляем заголовок
    title = "Список покупок"
    content.append(Paragraph(title, styles['TitleStyle']))
    content.append(Spacer(1, 24))

    # Добавляем основной текст
    content.append(Paragraph(text, styles['ContentStyle']))
    content.append(Spacer(1, 24))

    # Добавляем футер с информацией о сайте
    footer = f"Сгенерировано на сайте {settings.SITE_NAME}"
    content.append(Paragraph(footer, styles['FooterStyle']))

    # Собираем PDF
    pdf.build(content)

    return response
