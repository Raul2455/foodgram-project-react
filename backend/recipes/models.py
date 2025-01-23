from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Название ингредиента',
                            max_length=200, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Название тега', max_length=200, unique=True)
    slug = models.SlugField('Слаг', max_length=200, unique=True, blank=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField('Название рецепта', max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField('Изображение рецепта',
                              upload_to='recipes/images/')
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(1, message='Минимальное время — 1 минута.'),
            MaxValueValidator(
                1440, message='Максимальное время — 1440 минут (24 часа).')
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name

    def display_tags(self):
        """Возвращает строку с тегами для отображения в админке."""
        return ', '.join(tag.name for tag in self.tags.all())
    display_tags.short_description = 'Теги'


class IngredientInRecipe(models.Model):
    """Модель для связи ингредиентов и рецептов с указанием количества."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredient_in_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1,
                                      message='Минимальное количество — 1.')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class Cart(models.Model):
    """Модель корзины."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в корзину'
