from django.contrib import admin
from .models import ShoppingCart, FavoriteRecipe


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_editable = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_editable = ('recipe',)
    empty_value_display = '-пусто-'
