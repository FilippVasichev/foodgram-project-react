from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
    )
    color = models.CharField(
        max_length=16,
    )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=50,
        blank=False,
        null=False,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=10,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        max_length=200,
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
        max_length=500,
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
        validators=[MinValueValidator(1)]
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
