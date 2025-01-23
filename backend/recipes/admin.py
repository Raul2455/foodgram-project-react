from django.contrib import admin
from django.utils.html import format_html
from .models import Ingredient, Recipe, Tag, Cart, Favorite, IngredientInRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-пусто-'


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_favorite_count', 'cooking_time', 'pub_date')
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('author', 'tags', 'pub_date')
    inlines = (IngredientInRecipeInline,)
    readonly_fields = ('pub_date',)
    empty_value_display = '-пусто-'

    def is_favorite_count(self, obj):
        return obj.favorites.count()
    is_favorite_count.short_description = 'В избранном (раз)'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('favorites')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'