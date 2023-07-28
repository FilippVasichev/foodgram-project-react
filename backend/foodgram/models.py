from django.db import models
from users.models import User
from recipe.models import Recipe

class ShoppingCart(models.Model):
    cart_owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    products = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Продукты',
        related_name='products',
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Продуктовая корзина'
        verbose_name_plural = 'Продуктовые корзины'

    def __str__(self):
        return self.products.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    favorite_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite_recipe'], name='unique_fav_recipe'),
            models.CheckConstraint(
                name='foodgram_prevent_multi_fav_recipe',
                check=~models.Q(user=models.F('favorite_recipe')),
            )
        ]
