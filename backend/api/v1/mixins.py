from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class AbstractPostDeleteMixin(
    GenericViewSet,
    CreateModelMixin,
    DestroyModelMixin,
):
    """
    Абстрактый миксин для Корзины или Избранного.
    Обрабатывает http запросы "POST" и "DELETE".
    """

    permission_classes = [IsAuthenticated, ]
    lookup_field = 'id'
    pagination_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={
                'request': request,
                'kwargs': kwargs.get('id')
            }
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
