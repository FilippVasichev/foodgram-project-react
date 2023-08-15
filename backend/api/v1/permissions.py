from rest_framework.permissions import BasePermission


class AuthorOr403(BasePermission):
    """
    Пермишн ограничивающий права для http
    методов "PATCH" и "DELETE" при работе
    с обьектами рецепта
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, recipe):
        return (request.user == recipe.author or
                bool(request.user and request.user.is_staff))
