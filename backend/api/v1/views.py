from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipe.models import (FavoriteRecipe, Ingredient, IngredientQuantity,
                           Recipe, ShoppingCart, Tag)
from users.models import Follow, User

from .filters import RecipeFilterSet
from .paginators import CustomPageNumberPaginator
from .permissions import AuthorOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          CreateUserSubscriptionSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSubscriptionSerializer)
from .shopping_cart_list_generator import generate_shopping_cart_file


class DjoserCustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPaginator

    @action(methods=['post'], detail=True)
    def subscribe(self, request, id=None):
        serializer = CreateUserSubscriptionSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        get_object_or_404(Follow, user=request.user, author_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user)
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
    permission_classes = (AuthorOrReadOnly,)
    http_method_names = ['get', 'patch', 'delete', 'post']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author',
        ).prefetch_related(
            'recipe_ingredient__ingredient',
            'tags',
        ).annotate_user_fields(
            self.request.user.id
        )

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientQuantity.objects.filter(
            recipe__shopping_cart__user_id=request.user.id
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')
        return generate_shopping_cart_file(ingredients)

    @staticmethod
    def create_instance(serializer, pk, request):
        serializer = serializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk=None):
        return self.create_instance(FavoriteSerializer, pk, request)

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.create_instance(ShoppingCartSerializer, pk, request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        get_object_or_404(
            FavoriteRecipe,
            user=request.user,
            recipe_id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe_id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
