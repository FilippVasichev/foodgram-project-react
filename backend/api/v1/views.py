from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, \
    IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter

from foodgram.models import FavoriteRecipe, ShoppingCart
from recipe.models import Ingredient, Tag, Recipe
from users.models import Follow
from users.models import User

from .filters import RecipeFilterSet
from .paginators import CustomPageNumberPaginator
from .permissions import AuthorOr403
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer, \
    CreateUpdateRecipeSerializer, FavoriteSerializer, CustomUserSerializer, \
    UserSubscriptionSerializer, ShoppingCartSerializer


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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Follow,
                user=request.user,
                author_id=id
            )
            self.perform_destroy(subscribe)
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
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredient__ingredient',
        'tags'
    ).all()
    http_method_names = ['get', 'patch', 'delete', 'post']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_permissions(self):
        print(self.action)
        if self.action in ['partial_update', 'destroy']:
            return (AuthorOr403(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            context={'request': request},
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
def favoriterecipeview(request, id=None):
    if request.method == 'DELETE':
        favorite = get_object_or_404(
            FavoriteRecipe,
            recipe_id=id,
            user=request.user
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

@api_view(['DELETE', 'POST'])
def shoppingcartview(request, id=None):
    if request.method == 'DELETE':
        cart = get_object_or_404(ShoppingCart, recipe_id=id)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

# @api_view(['GET'])
# def download_shopping_cart(request):
#     user = request.user
#     shopping_list = user.shopping_cart.all()
#     ingredients = {}
#
#     for item in shopping_list:
#         print(item, '1')
#         ingredient = item.recipe.recipe_ingredient.all()
#         for ingredients_names in ingredient:
#             print(ingredients_names.amount, 'amount')
#         # amount = item.recipe.recipe_ingredient.amount
#         # # print(amount, '3')
#         return Response({"data": 'zalupa'})
