from django.db import models
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

from foodgram import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.NAME_FIELD_MAX_LENGTH,
    )
    color = ColorField()
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=constants.NAME_FIELD_MAX_LENGTH,
        null=False,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=constants.NAME_FIELD_MAX_LENGTH,
        null=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredients_unique_constraint',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='recipe'
    )
    name = models.CharField(
        max_length=constants.NAME_FIELD_MAX_LENGTH,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipe_tags',
        through='RecipeTag',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='ingredient',
        through='IngredientQuantity',
        through_fields=('recipe', 'ingredient'),
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True,
        null=True,
        default=None,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        null=False,
        blank=False,
        validators=[MinValueValidator(1)] ### Остановился здесь, добавить максимальный валидатор
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='tag'
    )

    def __str__(self):
        return self.tag.name


class AbstractUsersRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique_constraint',
            )
        ]

    def str(self):
        return f'{self.user} - {self.recipe}'


class FavoriteRecipe(AbstractUsersRecipe):
    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(AbstractUsersRecipe):
    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
