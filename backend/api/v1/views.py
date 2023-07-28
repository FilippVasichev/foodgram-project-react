from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import IngredientSerializer, TagSerializer
from recipe.models import Ingredient, Tag


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]



