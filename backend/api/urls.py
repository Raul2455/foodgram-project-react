"""Маршруты для API приложения."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientsViewSet, RecipesViewSet, TagsViewSet

# Определяем app_name для использования namespace
app_name = "api"

# Создаем экземпляр DefaultRouter для автоматической генерации URL
router = DefaultRouter()

# Регистрируем ViewSet для ингредиентов
router.register(
    r'ingredients',  # Префикс URL
    IngredientsViewSet,  # ViewSet
    basename='ingredients'  # Базовое имя для URL
)

# Регистрируем ViewSet для тегов
router.register(
    r'tags',  # Префикс URL
    TagsViewSet,  # ViewSet
    basename='tags'  # Базовое имя для URL
)

# Регистрируем ViewSet для рецептов
router.register(
    r'recipes',  # Префикс URL
    RecipesViewSet,  # ViewSet
    basename='recipes'  # Базовое имя для URL
)

# Основные URL-маршруты
urlpatterns = [
    # Включаем маршруты, сгенерированные роутером
    path('', include(router.urls)),
]
