from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram import constants


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        unique=True,
        blank=True,
        max_length=constants.EMAIL_FIELD_MAX_LENGTH,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'first_name',
        'last_name',
        'username',
    )

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'пользователи'
        ordering = ('date_joined',)

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
