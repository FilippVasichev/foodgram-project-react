from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorOrReadOnly(BasePermission):
    """
    Пермишн ограничивающий права для http
    методов "PATCH" и "DELETE" при работе
    с обьектами рецепта
    """

    def has_object_permission(self, request, view, recipe):
        return request.method in SAFE_METHODS or request.user == recipe.author
