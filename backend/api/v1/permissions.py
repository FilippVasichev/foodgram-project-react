from rest_framework.permissions import BasePermission, SAFE_METHODS

class AuthorOr403(BasePermission):
    """
    Пермишн для ограничения прав на PATCH
    и DELETE обьектов рецепта.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, recipe):
        return (request.user == recipe.author or
                bool(request.user and request.user.is_staff))
