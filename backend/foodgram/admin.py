from django.contrib import admin
from .models import ShoppingCart, FavoriteRecipe


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'cart_owner',
        'products',
    )
    search_fields = ('cart_owner',)
    list_editable = ('products',)
    empty_value_display = '-пусто-'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'favorite_recipe',
    )
    search_fields = ('user',)
    list_editable = ('favorite_recipe',)
    empty_value_display = '-пусто-'
