from django.db import models
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
        max_length=25,
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='tag'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient',
        through='IngredientQuantity',
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=500,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='food_images/',
        blank=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        null=False,
        blank=False,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.ingredient.name} - {self.quantity}'
