from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_subscribed = models.BooleanField(
        default=False,


    )

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
