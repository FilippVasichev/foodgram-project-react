from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientQuantity


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = IngredientQuantity
    extra = 1


class TagInLine(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
    )
    search_fields = (
        'name',
        'cocking_time',
    )
    empty_value_display = '-пусто-'
    inlines = [IngredientInline, TagInLine]
