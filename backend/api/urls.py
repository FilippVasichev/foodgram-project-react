from pprint import pprint

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from djoser.views import UserViewSet

from rest_framework.routers import DefaultRouter
from api.v1.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    favoriterecipeview,
    shoppingcartview,
    DjoserCustomUserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users', DjoserCustomUserViewSet, basename='users')

urlpatterns = [
    path(r'recipes/<int:id>/favorite/', favoriterecipeview),
    path(r'recipes/<int:id>/shopping_cart/', shoppingcartview),
    path(
        r'users/<int:id>/subscribe/',
        DjoserCustomUserViewSet.as_view({'post': 'subscribe'})
    ),
    # path(r'recipes/download_shopping_cart/', download_shopping_cart),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

pprint(urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)