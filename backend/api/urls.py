from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (DjoserCustomUserViewSet, IngredientViewSet,
                          RecipeViewSet, TagViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users', DjoserCustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
]
