from django_filters import FilterSet
from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag

class RecipesFilter(FilterSet):
    """
    Фильтр для модели Recipe.
    Позволяет фильтровать рецепты по названию, автору, тегам и времени приготовления.
    """

    # Фильтр по названию рецепта (регистронезависимый поиск)
    title = filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название рецепта'
    )

    # Фильтр по автору (по ID пользователя)
    author = filters.NumberFilter(
        field_name='author__id',
        label='ID автора'
    )

    # Фильтр по тегам (поиск по связанным тегам)
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Теги'
    )

    # Фильтр по минимальному времени приготовления
    cooking_time_min = filters.NumberFilter(
        field_name='cooking_time',
        lookup_expr='gte',
        label='Минимальное время приготовления'
    )

    # Фильтр по максимальному времени приготовления
    cooking_time_max = filters.NumberFilter(
        field_name='cooking_time',
        lookup_expr='lte',
        label='Максимальное время приготовления'
    )

    class Meta:
        model = Recipe
        fields = [
            'title',
            'author',
            'tags',
            'cooking_time_min',
            'cooking_time_max',
        ]
