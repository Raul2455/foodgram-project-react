from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения users."""

    # Указываем имя приложения
    name = 'users'

    # Настраиваем человекочитаемое имя для отображения в админке
    verbose_name = 'Пользователи'
