"""
Модуль для сериализации данных, связанных с рецептами,
пользователями, ингредиентами, тегами и подписками.
"""

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    ShoppingCart,
)
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    Используется для отображения данных пользователя.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на автора.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class SignupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    Проверяет запрещенные имена и уникальность email.
    """

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    banned_names = ("me", "admin", "ADMIN", "administrator", "moderator")

    class Meta:
        model = User
        fields = ("username", "email")

    def validate_username(self, value):
        """
        Проверяет, что имя пользователя не является запрещенным.
        """
        if value.lower() in self.banned_names:
            raise serializers.ValidationError(
                "Использование этого имени запрещено."
            )
        return value

    def validate_email(self, value):
        """
        Проверяет, что email уникален.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена.
    Проверяет учетные данные пользователя.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Проверяет учетные данные и возвращает токен.
        """
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = User.objects.filter(username=username).first()
            if user and user.check_password(password):
                return data
            raise serializers.ValidationError("Неверные учетные данные.")
        raise serializers.ValidationError(
            "Необходимо указать имя пользователя и пароль."
        )


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
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    # Переносим class Meta к началу определения класса RecipeWriteSerializer
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

    @transaction.atomic
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

    @transaction.atomic
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
        return RecipeSmallSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    Используется для добавления рецептов в корзину покупок.
    """

    class Meta:
        model = ShoppingCart
        fields = ["id", "user", "recipe"]
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=["user", "recipe"],
                message="Рецепт уже добавлен в корзину.",
            )
        ]

    def to_representation(self, instance):
        """
        Возвращает упрощенное представление рецепта.
        """
        return RecipeSmallSerializer(instance.recipe).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.
    Используется для работы с подписками.
    """

    class Meta:
        model = Subscription
        fields = ["user", "author"]
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["user", "author"],
                message="Вы уже подписаны на этого автора.",
            )
        ]

    def to_representation(self, instance):
        """
        Возвращает данные автора с рецептами.
        """
        return SubShowSerializer(instance.author, context=self.context).data


class SubShowSerializer(UserSerializer):
    """
    Сериализатор для отображения подписок с рецептами.
    Включает список рецептов автора.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["recipes", "recipes_count"]

    def get_recipes(self, obj):
        """
        Возвращает список рецептов автора.
        """
        request = self.context.get("request")
        recipes = obj.recipes.all()[:3]
        return RecipeSmallSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        """
        Возвращает общее количество рецептов автора.
        """
        return obj.recipes.count()
