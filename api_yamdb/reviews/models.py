from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from .validators import validate_username


USERNAME_MAX_LEN = 150
EMAIL_MAX_LEN = 254
ROLE_MAX_LEN = 20
CATEGORY_MAX_LEN_SLUG = 50
TITLE_MAX_LEN = 256


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
        return self.role == self.ADMIN

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField(
        max_length=EMAIL_MAX_LEN,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=CATEGORY_MAX_LEN_SLUG,
        verbose_name='Slug категории',
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$'
            )
        ]
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField(
        max_length=TITLE_MAX_LEN,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=CATEGORY_MAX_LEN_SLUG,
        verbose_name='Slug жанра',
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$'
            )
        ]
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(
        max_length=TITLE_MAX_LEN,
        verbose_name='Название'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год',
        validators=(
            MinValueValidator(0),
            MaxValueValidator(int(datetime.now().year))
        )
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        db_index=True,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Смежная модель для связи жанра и произведения."""

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        )
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            )]
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
