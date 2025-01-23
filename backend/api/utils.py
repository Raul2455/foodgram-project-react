"""
Модуль для работы с генерацией PDF-документов.

Используется для создания PDF-файлов, таких как списки покупок и рецепты.
"""

import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from foodgram.settings import MEDIA_ROOT, SITE_NAME


# Регистрация шрифта
pdfmetrics.registerFont(
    TTFont('DejaVuSerif', os.path.join(MEDIA_ROOT, 'fonts/DejaVuSerif.ttf'))
)


def generate_pdf(filename, title, content):
    """
    Генерирует PDF-документ с заданным заголовком и содержимым.

    :param filename: Имя файла для сохранения PDF.
    :param title: Заголовок документа.
    :param content: Содержимое документа (список строк или абзацев).
    :return: Путь к сохраненному PDF-файлу.
    """
    # Создаем документ
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Получаем стандартные стили
    styles = getSampleStyleSheet()

    # Стиль для заголовка
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],  # Использование стандартного стиля
        fontName='DejaVuSerif',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=1 * cm,
        textColor=colors.darkblue  # Использование colors
    )

    # Стиль для основного текста
    text_style = ParagraphStyle(
        name='TextStyle',
        parent=styles['BodyText'],  # Использование стандартного стиля
        fontName='DejaVuSerif',
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=0.5 * cm,
        textColor=colors.black  # Использование colors
    )

    # Элементы документа
    elements = []

    # Добавляем заголовок
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Добавляем содержимое
    for item in content:
        elements.append(Paragraph(item, text_style))
        elements.append(Spacer(1, 0.2 * cm))

    # Собираем документ
    doc.build(elements)

    return filename


def generate_shopping_list_pdf(user, ingredients):
    """
    Генерирует PDF-документ со списком покупок для пользователя.

    :param user: Пользователь, для которого создается список.
    :param ingredients: Список ингредиентов в формате
    [{'name': str, 'amount': str}].
    :return: Путь к сохраненному PDF-файлу.
    """
    # Название файла
    filename = os.path.join(
        MEDIA_ROOT, f'shopping_lists/{user.username}_shopping_list.pdf'
    )

    # Заголовок документа
    title = f'Список покупок для {user.username} ({SITE_NAME})'

    # Содержимое документа
    content = [f"{item['name']} - {item['amount']}" for item in ingredients]

    # Генерация PDF
    return generate_pdf(filename, title, content)


def generate_recipe_pdf(recipe):
    """
    Генерирует PDF-документ с информацией о рецепте.

    :param recipe: Рецепт (объект модели Recipe).
    :return: Путь к сохраненному PDF-файлу.
    """
    # Название файла
    filename = os.path.join(MEDIA_ROOT, f'recipes/{recipe.id}_recipe.pdf')

    # Заголовок документа
    title = f'Рецепт: {recipe.title} ({SITE_NAME})'  # Использование SITE_NAME

    # Содержимое документа
    content = [
        f"Автор: {recipe.author.username}",
        f"Описание: {recipe.description}",
        "Ингредиенты:",
        *[
            f"- {ingredient.name} "  # Название ингредиента
            f"({ingredient.amount} "  # Количество
            f"{ingredient.measurement_unit})"  # Единица измерения
            for ingredient in recipe.ingredients.all()
        ],
        f"Время приготовления: {recipe.cooking_time} минут",
    ]

    # Генерация PDF
    return generate_pdf(filename, title, content)
