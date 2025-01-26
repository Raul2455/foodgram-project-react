from django.apps import AppConfig


class RecipesConfig(AppConfig):
    # Указываем имя приложения
    name = 'recipes'

    # Настраиваем человекочитаемое имя для отображения в админке
    verbose_name = 'Управление рецептами'
