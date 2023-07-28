from django.urls import path, include
from django.conf import settings
from djoser.views import UserViewSet

from rest_framework.routers import DefaultRouter
from api.v1.views import IngredientViewSet, TagViewSet

router_v1 = DefaultRouter()
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]