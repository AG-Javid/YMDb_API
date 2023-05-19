from django.db import models

from django.contrib.auth.models import AbstractUser

from .validators import validate_username

USERNAME_MAX_LEN = 150
EMAIL_MAX_LEN = 254
ROLE_MAX_LEN = 20


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    username = models.CharField(
        unique=True,
        max_length=USERNAME_MAX_LEN,
        validators=(validate_username,),
        verbose_name='Ник пользователя',
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LEN,
        verbose_name='Email адрес'
    )
    first_name = models.CharField(
        max_length=USERNAME_MAX_LEN,
        blank=True,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=USERNAME_MAX_LEN,
        blank=True,
        verbose_name='Фамилия пользователя'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О пользователе'
    )
    role = models.CharField(
        max_length=ROLE_MAX_LEN,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Пользовательская роль'
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
