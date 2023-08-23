from django_filters import rest_framework as filters

from recipe.models import Recipe


class RecipeFilterSet(filters.FilterSet):
    """
    Позволяет применять различные фильтры для поиска рецептов в списке.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', )
    is_favorited = filters.BooleanFilter(method='filter_is_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )

    def filter_is_favorite(self, queryset, name, value):
        """
        Применяет фильтр для избранных рецептов текущего пользователя.
        """
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Применяет фильтр для рецептов в корзине текущего пользователя.
        """
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
