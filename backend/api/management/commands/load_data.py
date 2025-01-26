import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда Django для загрузки данных из JSON-файлов в базу данных.
    Поддерживает загрузку ингредиентов.
    """

    help = "Загружает данные из JSON-файлов в базу данных."

    def handle(self, *args, **options):
        """
        Основной метод, который выполняется при вызове команды.
        """
        # Путь к файлу ингредиентов
        ingredients_file = os.path.join(
            settings.BASE_DIR.parent, "data", "ingredients.json")

        # Загрузка ингредиентов
        self.import_ingredients(ingredients_file)

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены!"))

    def import_ingredients(self, ingredients_file):
        """
        Загружает ингредиенты из JSON-файла в базу данных.

        :param ingredients_file: Путь к файлу с ингредиентами.
        """
        if not os.path.exists(ingredients_file):
            self.stdout.write(
                self.style.ERROR(f"Файл {ingredients_file} не найден!")
            )
            return

        try:
            with open(ingredients_file, "r", encoding="utf-8") as file:
                ingredients_data = json.load(file)
                for ingredient_data in ingredients_data:
                    self.create_ingredient(ingredient_data)
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    f"Файл {ingredients_file} содержит некорректный JSON!"
                )
            )

    def create_ingredient(self, ingredient_data):
        """
        Создает ингредиент в базе данных.

        :param ingredient_data: Данные ингредиента
        (словарь с ключами 'name' и 'measurement_unit').
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
