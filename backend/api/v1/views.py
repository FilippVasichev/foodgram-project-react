import authentication as authentication
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin

from foodgram.models import FavoriteRecipe
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer, \
    CreateUpdateRecipeSerializer, FavoriteSerializer
from recipe.models import Ingredient, Tag, Recipe


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class RecipeViewSet(ModelViewSet):
    """
    добавить status=status.HTTP
    """
    permission_classes = [AllowAny]
    queryset = Recipe.objects.prefetch_related(
        'recipe_ingredient__ingredient',
        'tags'
    ).all()
    pagination_class = None
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'patch', 'delete', 'post']

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            context={'request':request},
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            get_object_or_404(self.get_queryset(), pk=kwargs.get('pk')),
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        serializer = CreateUpdateRecipeSerializer(
            recipe,
            context={'request': request},
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        serializer = CreateUpdateRecipeSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        self.perform_destroy(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE', 'POST'])
def favoriterecipe(request, id):
    if request.method == 'DELETE':
        favorite = get_object_or_404(FavoriteRecipe, recipe_id=id)
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




# class FavoriteViewSet(ModelViewSet):
#     queryset = FavoriteRecipe.objects.all()
#     serializer_class = FavoriteSerializer
#
#     @action(methods=['POST', 'DELETE'], detail=True)
#     def favoriterecipe(self, request, id):
#         print(id)
#         if request.method == 'DELETE':
#             favorite = get_object_or_404(FavoriteRecipe, recipe_id=id)
#             favorite.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#
#         if request.method == 'POST':
#             serializer = FavoriteSerializer(
#                 data=request.data,
#                 context={
#                     'request': request,
#                     'kwargs': id
#                 }
#             )
#             if serializer.is_valid(raise_exception=True):
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(
    #         data=request.data,
    #         context={
    #             'request': request,
    #             'kwargs': kwargs
    #                  }
    #     )
    #     if serializer.is_valid(raise_exception=True):
    #         self.perform_create(serializer)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
    # def destroy(self, request, *args, **kwargs):
    #     recipe_id = kwargs.get('id')
    #     favorite = get_object_or_404(self.get_queryset(), recipe_id=recipe_id)
    #     self.perform_destroy(favorite)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def perform_destroy(self, instance):
#         instance.delete()
#
# class FavoriteApiView(GenericViewSet, DestroyModelMixin, CreateModelMixin):
#     queryset = FavoriteRecipe
#     pagination_class = None
#     permission_classes = [AllowAny]
#     serializer_class = FavoriteSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             data=request.data,
#             context={
#                 'request': request,
#                 'kwargs': kwargs
#             }
#         )
#         if serializer.is_valid(raise_exception=True):
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#     def destroy(self, request, *args, **kwargs):
#         recipe_id = args.get('id')
#         favorite = get_object_or_404(self.get_queryset(), recipe_id=recipe_id)
#         self.perform_destroy(favorite)
#         return Response(status=status.HTTP_204_NO_CONTENT)




