from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram import constants


class User(AbstractUser):
    email = models.EmailField(
        'Email адрес',
        unique=True,
        null=False,
        max_length=constants.EMAIL_FIELD_MAX_LENGTH,
    )
    username = models.CharField(
        'Юзернейм',
        max_length=constants.USER_NAME_MAX_LENGTH,
        unique=True,
        null=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=constants.USER_NAME_MAX_LENGTH,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=constants.USER_NAME_MAX_LENGTH,
        null=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'first_name',
        'last_name',
        'username',
    )

    class Meta:
        ordering = ('pk',)
        verbose_name = 'пользователя'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        null=False,
        on_delete=models.CASCADE,
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        null=False,
        on_delete=models.CASCADE,
        help_text='Автор контента'
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'),
            models.CheckConstraint(
                name='follow_prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            )
        ]

    def __str__(self) -> str:
        return (f'Пользователь: {self.user.username},'
                f' подписан на: {self.author.username}')
