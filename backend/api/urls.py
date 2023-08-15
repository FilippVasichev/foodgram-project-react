from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    favoriterecipeview,
    shoppingcartview,
    DjoserCustomUserViewSet,
    download_shopping_cart,
)

router_v1 = DefaultRouter()
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users', DjoserCustomUserViewSet, basename='users')

recipe_prefix = 'recipes/'

urlpatterns = [
    path(f'{recipe_prefix}<int:id>/favorite/', favoriterecipeview),
    path(f'{recipe_prefix}<int:id>/shopping_cart/', shoppingcartview),
    path(f'{recipe_prefix}download_shopping_cart/', download_shopping_cart),
    path(
        'users/<int:id>/subscribe/',
        DjoserCustomUserViewSet.as_view(
            {
                'post': 'subscribe',
                'delete': 'subscribe',
            }
        ),
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)