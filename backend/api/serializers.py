"""
Модуль для сериализации данных, связанных с рецептами, пользователями и другими моделями.
"""

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag
)
from users.models import User


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Favorite.
    Используется для добавления рецептов в избранное.
    """

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное.'
            )
        ]

    def to_representation(self, instance):
        """
        Возвращает упрощенное представление рецепта.
        """
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.title,
            'image': instance.recipe.image.url if instance.recipe.image else None,
            'cooking_time': instance.recipe.cooking_time
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Используется для отображения данных пользователя.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TagsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    Используется для отображения тегов.
    """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Используется для отображения ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи ингредиентов в рецепт.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class RecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.
    Используется для отображения рецептов.
    """

    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_ingredients(self, obj):
        """
        Возвращает список ингредиентов для рецепта.
        """
        return [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.amount
            }
            for ingredient in obj.ingredients_in_recipe.all()
        ]

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное у текущего пользователя.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в корзину у текущего пользователя.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class RecipeSmallSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для модели Recipe.
    Используется для отображения краткой информации о рецепте.
    """

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipesSerializerCreate(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    """

    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'tags', 'ingredients', 'image',
            'text', 'cooking_time'
        ]

    def validate_ingredients(self, value):
        """
        Проверяет, что ингредиенты уникальны и их количество больше нуля.
        """
        if not value:
            raise serializers.ValidationError('Добавьте хотя бы один ингредиент.')
        ingredients = [item['id'] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError('Ингредиенты должны быть уникальными.')
        return value

    def create(self, validated_data):
        """
        Создает рецепт с ингредиентами и тегами.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет рецепт с ингредиентами и тегами.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.ingredients_in_recipe.all().delete()
        self._create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def _create_ingredients(self, recipe, ingredients):
        """
        Создает записи ингредиентов для рецепта.
        """
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
        )


class ActionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для действий с рецептами (избранное, корзина).
    """

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe']
