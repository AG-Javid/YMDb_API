from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

USERNAME_MAX_LEN = 150
EMAIL_MAX_LEN = 254
ROLE_MAX_LEN = 20


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    MODERATOR = 'moderator', 'Модератор'
    USER = 'user', 'Пользователь'


class User(AbstractUser):
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
        choices=UserRole.choices,
        default='user',
        blank=True,
        verbose_name='Пользовательская роль'
    )
    confirmation_code = models.CharField(
        max_length=EMAIL_MAX_LEN,
        null=True,
        blank=False,
        verbose_name='Код подтверждения'
    )

    @property
    def is_admin(self):
        return (
            self.role == UserRole.ADMIN or self.is_staff or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
