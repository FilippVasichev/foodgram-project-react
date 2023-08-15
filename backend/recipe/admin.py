from django.contrib.admin import (
    TabularInline,
    ModelAdmin,
    register,
    display,
    site
)
from django.contrib.auth.models import Group

from .models import Tag, Ingredient, Recipe


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
    min_num = 3


class TagInLine(TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'author',
        'name',
        'favorite_count',
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


site.unregister(Group)
