"""
Модуль для настройки URL-маршрутов проекта Foodgram.

Этот модуль определяет основные маршруты для API, административной панели
и аутентификации (например, Djoser).
"""

from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

# Простое представление для главной страницы


def index(request):
    return HttpResponse("""
        <html>
        <head>
            <title>Foodgram</title>
        </head>
        <body>
            <h1>Добро пожаловать в Foodgram!</h1>
            <p>Это главная страница вашего проекта.</p>
            <p>Перейдите в <a href="/api/">API</a> или
            <a href="/admin/">админку</a>.</p>
        </body>
        </html>
    """)

# Основные URL-маршруты приложения


urlpatterns = [
    # Главная страница
    path("", index, name="index"),  # Главная страница

    # Маршруты для API
    path("api/", include("api.urls", namespace="api")),

    # Маршруты для административной панели Django
    path("admin/", admin.site.urls),

    # Маршруты для аутентификации (Djoser)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
