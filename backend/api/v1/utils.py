from django.db.models import Sum
from django.http import HttpResponse

from recipe.models import IngredientQuantity


def generate_shopping_cart_file(user):
    ingredients = IngredientQuantity.objects.filter(
        recipe__shopping_cart__user_id=user.id
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit',
    ).annotate(
        amount=Sum('amount')
    ).order_by('ingredient__name')
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{user.username}_shopping_list.txt"'
    )
    for ingredient in ingredients:
        line = (
            f"{ingredient['ingredient__name']}:"
            f" {ingredient['amount']}"
            f" {ingredient['ingredient__measurement_unit']}\n"
        )
        response.write(line)
    return response
