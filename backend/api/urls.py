from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from djoser.views import UserViewSet

from rest_framework.routers import DefaultRouter
from api.v1.views import IngredientViewSet, TagViewSet, RecipeViewSet, favoriterecipe

router_v1 = DefaultRouter()
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
# router_v1.register(r'recipes/<int:id>/favorite/', FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/favorite/', favoriterecipe, name='delete-favorite'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)