from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        blank=True,
        max_length=254,
    )

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        blank=False,
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