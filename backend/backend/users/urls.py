from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

# Создаем экземпляр DefaultRouter для автоматической генерации URL-адресов
router = DefaultRouter()

# Регистрируем ViewSet для работы с пользователями
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    # Подключаем URL-адреса, сгенерированные роутером
    path('', include(router.urls)),

    # Подключаем стандартные эндпоинты для аутентификации (например, токены)
    path('auth/', include('djoser.urls.authtoken')),
]
