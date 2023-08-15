from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


class AdminUser(BaseUserAdmin):
    change_password_template = "admin/auth/user/change_password.html"


@admin.register(User)
class UserAdmin(AdminUser):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
    )
    list_filter = (
        'email',
        'username',
        'is_staff',
    )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username', 'author__username')
