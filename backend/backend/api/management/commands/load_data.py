import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """
    Команда Django для загрузки данных из JSON-файлов в базу данных.
    Поддерживает загрузку тегов и ингредиентов.
    """

    help = "Загружает данные из JSON-файлов в базу данных."

    def add_arguments(self, parser):
        """
        Добавляет аргументы для команды.
        """
        parser.add_argument(
            "--tags",
            type=str,
            default="tags.json",
            help="Имя файла с тегами (по умолчанию: tags.json)",
        )
        parser.add_argument(
            "--ingredients",
            type=str,
            default="ingredients.json",
            help="Имя файла с ингредиентами (по умолчанию: ingredients.json)",
        )

    def handle(self, *args, **options):
        """
        Основной метод, который выполняется при вызове команды.
        """
        tags_file = options["tags"]
        ingredients_file = options["ingredients"]

        # Загрузка тегов
        self.import_tags(tags_file)
        # Загрузка ингредиентов
        self.import_ingredients(ingredients_file)

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены!"))

    def import_tags(self, tags_file):
        """
        Загружает теги из JSON-файла в базу данных.

        :param tags_file: Имя файла с тегами.
        """
        file_path = Path(settings.BASE_DIR) / "data" / tags_file
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл {tags_file} не найден!"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                tags_data = json.load(file)
                for tag_data in tags_data:
                    self.create_tag(tag_data)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    f"Файл {tags_file} содержит некорректный JSON!")
            )

    def import_ingredients(self, ingredients_file):
        """
        Загружает ингредиенты из JSON-файла в базу данных.

        :param ingredients_file: Имя файла с ингредиентами.
        """
        file_path = Path(settings.BASE_DIR) / "data" / ingredients_file
        # Использование os для проверки существования файла
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(
                f"Файл {ingredients_file} не найден!"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                ingredients_data = json.load(file)
                for ingredient_data in ingredients_data:
                    self.create_ingredient(ingredient_data)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    f"Файл {ingredients_file} содержит некорректный JSON!"
                )
            )

    def create_tag(self, tag_data):
        """
        Создает тег в базе данных.

        :param tag_data: Данные тега (словарь с ключами 'name' и 'color').
        """
        try:
            Tag.objects.create(
                name=tag_data["name"],
                color=tag_data["color"],
                slug=tag_data.get("slug", ""),  # Опциональное поле
            )
            self.stdout.write(
                self.style.SUCCESS(f"Тег '{tag_data['name']}' успешно создан!")
            )
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING(f"Тег '{tag_data['name']}' уже существует!")
            )

    def create_ingredient(self, ingredient_data):
        """
        Создает ингредиент в базе данных.

        :param ingredient_data: Данные ингредиента (словарь с ключами 'name' и
    'measurement_unit').
        """
        try:
            Ingredient.objects.create(
                name=ingredient_data["name"],
                measurement_unit=ingredient_data["measurement_unit"],
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Ингредиент '{ingredient_data['name']}' успешно создан!"
                )
            )
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING(
                    f"Ингредиент '{ingredient_data['name']}' уже существует!"
                )
            )
