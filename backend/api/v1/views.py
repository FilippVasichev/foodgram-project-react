from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipe.models import Ingredient, Tag, Recipe, FavoriteRecipe, ShoppingCart
from users.models import Follow
from users.models import User
from .filters import RecipeFilterSet
from .paginators import CustomPageNumberPaginator
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    CreateUpdateRecipeSerializer,
    FavoriteSerializer,
    CustomUserSerializer,
    UserSubscriptionSerializer,
    ShoppingCartSerializer,
)


class DjoserCustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPaginator

    @action(methods=['DELETE', 'POST'], detail=True)
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            try:
                serializer = UserSubscriptionSerializer(
                    Follow.objects.create(
                        user=request.user,
                        author_id=id
                    ),
                    context={'request': request},
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Follow,
            user=request.user,
            author_id=id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        subscriptions = Follow.objects.filter(user_id=request.user.id)
        paginated_subscription = self.paginate_queryset(subscriptions)
        serializer = UserSubscriptionSerializer(
            paginated_subscription,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('$name',)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """
    добавить status=status.HTTP
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.select_related(
        'author',
    ).prefetch_related(
        'recipe_ingredient__ingredient',
        'tags'
    ).all()
    http_method_names = ['get', 'patch', 'delete', 'post']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer


@api_view(['DELETE', 'POST'])
def favoriterecipeview(request, id=None):
    if request.method == 'POST':
        serializer = FavoriteSerializer(
            data=request.data,
            context={
                'request': request,
                'kwargs': id
            }
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    get_object_or_404(
        FavoriteRecipe,
        recipe_id=id,
        user=request.user,
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
def shoppingcartview(request, id=None):
    if request.method == 'POST':
        serializer = ShoppingCartSerializer(
            data=request.data,
            context={
                'request': request,
                'kwargs': id,
            }
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    get_object_or_404(
        ShoppingCart,
        recipe_id=id,
        user=request.user,
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    user = request.user
    shopping_list = user.shopping_cart.all()
    ingredients_list = {}
    for item in shopping_list:
        ingredients = item.recipe.recipe_ingredient.all()
        for ingredient_quantity in ingredients:
            ingredient = ingredient_quantity.ingredient
            amount = ingredient_quantity.amount
            if ingredient in ingredients_list:
                ingredients_list[ingredient] += amount
            else:
                ingredients_list[ingredient] = amount
    pprint(ingredients_list)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{user.username}_shopping_list.txt"'
    )
    for ingredient, amount in ingredients_list.items():
        line = f"{ingredient}: {amount}\n"
        response.write(line)
    return response
