"""
Модуль для настройки административной панели Django.
Регистрирует модели для управления через админку.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Ingredient, Recipe, Tag, Cart, Favorite, IngredientInRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Ingredient.
    Позволяет управлять ингредиентами.
    """
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Tag.
    Позволяет управлять тегами.
    """
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-пусто-'


class IngredientInRecipeInline(admin.TabularInline):
    """
    Встроенная панель для добавления ингредиентов в рецепт.
    """
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Recipe.
    Позволяет управлять рецептами.
    """
    list_display = ('name', 'author', 'is_favorite_count',
                    'cooking_time', 'pub_date', 'image_preview')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author', 'tags', 'pub_date')
    inlines = (IngredientInRecipeInline,)
    readonly_fields = ('pub_date', 'image_preview')
    empty_value_display = '-пусто-'

    def is_favorite_count(self, obj):
        """
        Возвращает количество добавлений рецепта в избранное.
        """
        return obj.favorites.count()
    is_favorite_count.short_description = 'В избранном (раз)'

    def image_preview(self, obj):
        """
        Возвращает HTML-превью изображения рецепта.
        """
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.image.url
            )
        return '-пусто-'
    image_preview.short_description = 'Превью изображения'

    def get_queryset(self, request):
        """
        Оптимизация запросов к базе данных.
        """
        return super().get_queryset(request).prefetch_related('favorites')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Cart.
    Позволяет управлять корзиной покупок.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Favorite.
    Позволяет управлять избранными рецептами.
    """
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """
    Административная панель для модели IngredientInRecipe.
    Позволяет управлять связью ингредиентов и рецептов.
    """
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'
