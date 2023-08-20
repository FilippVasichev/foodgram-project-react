from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipe.models import Ingredient, Tag, Recipe, FavoriteRecipe, ShoppingCart
from users.models import Follow
from users.models import User
from .filters import RecipeFilterSet
from .paginators import CustomPageNumberPaginator
from .permissions import AuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    CreateUpdateRecipeSerializer,
    FavoriteSerializer,
    CustomUserSerializer,
    UserSubscriptionSerializer,
    ShoppingCartSerializer, CreateUserSubscriptionSerializer,
)


class DjoserCustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPaginator


    @action(methods=['post'], detail=True)
    def subscribe(self, request, id=None):
        user = request.user
        serializer = CreateUserSubscriptionSerializer(
            data={'request': request},
            context={
                'user': user,
                'author': id,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author_id=id, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        get_object_or_404(Follow, user=request.user, author_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user.id)
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
    permission_classes = (AuthorOrReadOnly,)
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

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
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

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{user.username}_shopping_list.txt"'
        )
        for ingredient, amount in ingredients_list.items():
            line = f"{ingredient}: {amount}\n"
            response.write(line)
        return response

    @staticmethod
    def create_instance(serializer, pk, request):
        _serializer = serializer(
            data={'request': request,},
            context={
                'user_id': request.user.id,
                'recipe_id': pk,
            }
        )
        _serializer.is_valid(raise_exception=True)
        _serializer.save()
        return Response(_serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        self.create_instance(FavoriteSerializer, pk, request)

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk):
        self.create_instance(ShoppingCartSerializer, request, pk)

# @api_view(['DELETE', 'POST'])
# def favoriterecipeview(request, id=None):
#     if request.method == 'POST':
#         serializer = FavoriteSerializer(
#             data=request.data,
#             context={
#                 'request': request,
#                 'kwargs': id
#             }
#         )
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     get_object_or_404(
#         FavoriteRecipe,
#         recipe_id=id,
#         user=request.user,
#     ).delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# @api_view(['DELETE', 'POST'])
# def shoppingcartview(request, id=None):
#     if request.method == 'POST':
#         serializer = ShoppingCartSerializer(
#             data=request.data,
#             context={
#                 'request': request,
#                 'kwargs': id,
#             }
#         )
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     get_object_or_404(
#         ShoppingCart,
#         recipe_id=id,
#         user=request.user,
#     ).delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)
