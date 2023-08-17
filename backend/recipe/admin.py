from django.contrib.admin import (
    TabularInline,
    ModelAdmin,
    register,
    display,
    site
)
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group

from .models import Tag, Ingredient, Recipe, ShoppingCart, FavoriteRecipe


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    empty_value_display = '-пусто-'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientInline(TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


class TagInLine(TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'author',
        'name',
        'recipe_image',
        'favorite_count',
        'recipe_ingredients',
        'recipe_tags',
    )
    list_filter = (
        'name',
        'tags',
        'author',
    )
    empty_value_display = '-пусто-'
    inlines = [IngredientInline, TagInLine]

    @display(
        description='Сколько раз в избранном',
        empty_value='-пусто-',
    )
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @display(
        description='Ингридиенты',
        empty_value='-пусто-',
    )
    def recipe_ingredients(self, recipe):
        return list(recipe.ingredients.all())

    @display(
        description='Тэги',
        empty_value='-пусто-',
    )
    def recipe_tags(self, recipe):
        return list(recipe.tags.all())

    @display(
        description='Картинка',
        empty_value='-пусто-',
    )
    def recipe_image(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src={recipe.image.url} width="80" height="60">'
            )


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_editable = ('recipe',)
    empty_value_display = '-пусто-'


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_editable = ('recipe',)
    empty_value_display = '-пусто-'


site.unregister(Group)
