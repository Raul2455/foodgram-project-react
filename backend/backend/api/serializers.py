"""
Модуль для сериализации данных, связанных с рецептами,
пользователями, ингредиентами и тегами.
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
    Tag,
)
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Используется для отображения данных пользователя.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    Используется для отображения тегов.
    """

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Используется для отображения ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи ингредиентов и рецептов.
    Используется для отображения количества ингредиентов в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ["id", "name", "measurement_unit", "amount"]


class RecipeSmallSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для отображения краткой информации о рецепте.
    Используется в подписках и других местах, где нужен минимум данных.
    """

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных рецепта.
    Используется для отображения полной информации о рецепте.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source="ingredients_in_recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное у текущего пользователя.
        """
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в корзину у текущего пользователя.
        """
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    Используется для обработки данных при создании или изменении рецепта.
    """

    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    author = SlugRelatedField(
        slug_field="username", read_only=True
    )  # Использование SlugRelatedField

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "tags",
            "ingredients",
            "image",
            "text",
            "cooking_time",
            "author",
        ]

    def validate_ingredients(self, value):
        """
        Проверяет, что ингредиенты уникальны и их количество больше нуля.
        """
        if not value:
            raise serializers.ValidationError(
                "Добавьте хотя бы один ингредиент."
            )
        ingredients = [item["id"] for item in value]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными."
            )
        return value

    @transaction.atomic  # Использование транзакций
    def create(self, validated_data):
        """
        Создает рецепт с ингредиентами и тегами.
        """
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic  # Использование транзакций
    def update(self, instance, validated_data):
        """
        Обновляет рецепт с ингредиентами и тегами.
        """
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
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
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Favorite.
    Используется для добавления рецептов в избранное.
    """

    class Meta:
        model = Favorite
        fields = ["id", "user", "recipe"]
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["user", "recipe"],
                message="Рецепт уже добавлен в избранное.",
            )
        ]

    def to_representation(self, instance):
        """
        Возвращает упрощенное представление рецепта.
        """
        return {
            "id": instance.recipe.id,
            "name": instance.recipe.name,
            "image": instance.recipe.image.url,
            "cooking_time": instance.recipe.cooking_time,
        }


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    Используется для добавления рецептов в корзину покупок.
    """

    class Meta:
        model = Favorite
        fields = ["id", "user", "recipe"]
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["user", "recipe"],
                message="Рецепт уже добавлен в корзину.",
            )
        ]

    def to_representation(self, instance):
        """
        Возвращает упрощенное представление рецепта.
        """
        return {
            "id": instance.recipe.id,
            "name": instance.recipe.name,
            "image": instance.recipe.image.url,
            "cooking_time": instance.recipe.cooking_time,
        }
