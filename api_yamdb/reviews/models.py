from datetime import datetime

from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import User

MAX_LEN_SLUG = 50
NAME_CATEGORY_MAX_LEN = 254
NAME_MAX_LEN = 256


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField(
        max_length=NAME_CATEGORY_MAX_LEN,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_SLUG,
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
        max_length=NAME_MAX_LEN,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_SLUG,
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
        max_length=NAME_MAX_LEN,
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

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'


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
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть выше 10')
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
