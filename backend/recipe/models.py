from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

from foodgram import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
    )
    color = ColorField('Цвет тэга')
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
        db_index=True,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
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


class RecipeQuerySet(models.QuerySet):
    """
    Возвращает queryset с аннотациями,
    связанными с избранными рецептами и корзиной для покупок,
    если пользователь аутентифицирован.
    Если пользователь анонимен, метод возвращает базовый queryset.
    """
    def annotate_user_fields(self, user_id):
        favorited = FavoriteRecipe.objects.filter(
            user=user_id,
            recipe_id=OuterRef('pk')
        )
        shopping_cart = ShoppingCart.objects.filter(
            user=user_id,
            recipe_id=OuterRef('pk')
        )
        return self.annotate(
            is_favorited=Exists(favorited),
            is_in_shopping_cart=Exists(shopping_cart)
        ) if user_id else super().annotate()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=constants.RECIPE_NAME_MAX_LENGTH,
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
    text = models.TextField('Текст')
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        blank=True,
        null=True,
        default=None,
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                constants.MIN_COOKING_TIME,
                'Укажите время приготовления'
            ),
            MaxValueValidator(
                constants.MAX_COOKING_TIME,
                'Слишком большое время приготовления'
            )
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = (
            '-pub_date',
            'author',
        )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                constants.MIN_INGREDIENT_AMOUNT,
                'Укажите кол-во ингредиента.'
            ),
            MaxValueValidator(
                constants.MAX_INGREDIENT_AMOUNT,
                'Слишком большое число.'
            )
        )
    )

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=models.CASCADE,
        related_name='tag'
    )

    def __str__(self):
        return self.tag.name


class AbstractUsersRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
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
