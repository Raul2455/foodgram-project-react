"""
Модуль для обработки запросов API,
связанных с рецептами, ингредиентами и тегами.
"""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.filter import RecipesFilter
from api.mixins import ReadOnlyViewSet
from api.utils import generate_shopping_list_pdf
from api.permissions import AuthorAdminOrReadOnlyPermission
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)


class IngredientFilter(SearchFilter):
    """
    Фильтр для поиска ингредиентов по названию.
    """
    search_param = 'name'  # Параметр для поиска


class TagsViewSet(ReadOnlyViewSet):
    """
    ViewSet для работы с тегами.
    Поддерживает только чтение (GET-запросы).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Отключаем пагинацию для тегов


class IngredientsViewSet(ReadOnlyViewSet):
    """
    ViewSet для работы с ингредиентами.
    Поддерживает только чтение (GET-запросы).
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter]
    search_fields = ['^name']  # Поиск по началу названия
    pagination_class = None  # Отключаем пагинацию для ингредиентов


class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.
    Поддерживает все CRUD-операции.
    """
    queryset = Recipe.objects.all()
    permission_classes = [AuthorAdminOrReadOnlyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из избранного.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            # Проверяем, не добавлен ли рецепт уже в избранное
            favorite, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response(
                    {'detail': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            # Удаляем рецепт из избранного
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if not favorite.exists():
                return Response(
                    {'detail': 'Рецепт не найден в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из корзины покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            # Проверяем, не добавлен ли рецепт уже в корзину
            cart, created = Cart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response(
                    {'detail': 'Рецепт уже в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShoppingCartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            # Удаляем рецепт из корзины
            cart = Cart.objects.filter(user=user, recipe=recipe)
            if not cart.exists():
                return Response(
                    {'detail': 'Рецепт не найден в корзине.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Генерирует и возвращает PDF-файл со списком покупок.
        """
        user = request.user

        # Получаем список ингредиентов из корзины
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__carts__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        # Формируем данные для PDF
        shopping_list = [
            {
                'name': item['ingredient__name'],
                'amount': (
                    f"{item['total_amount']} "
                    f"{item['ingredient__measurement_unit']}"
                )
            }
            for item in ingredients
        ]

        # Генерируем PDF
        pdf_path = generate_shopping_list_pdf(user, shopping_list)

        # Возвращаем PDF как ответ
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(
                pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="{user.username}_shopping_list.pdf"'
            )
            return response
