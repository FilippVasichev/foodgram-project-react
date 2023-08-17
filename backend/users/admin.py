from django.contrib.admin import (
    register,
    display,
    ModelAdmin,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


@register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'recipe_count',
        'follow_count',
    )
    list_filter = (
        'email',
        'username',
        'is_staff',
    )
    empty_value_display = '-пусто-'

    @display(
        description='кол-во рецептов',
        empty_value='-пусто-',
    )
    def recipe_count(self, user):
        return user.recipe.count()

    @display(
        description='кол-во подписок',
        empty_value='-пусто-',
    )
    def follow_count(self, user):
        return user.following.count()

@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username', 'author__username')
