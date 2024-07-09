from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import MAX_NAME_LENGTH, MAX_SLUG_LENGTH, CHAR_OUTPUT_LIMIT

from django.contrib.auth.models import AbstractUser
from django.core import validators


class MyUser(AbstractUser):
    """Пользовательская модель юзера."""
    ROLE_CHOICES = [
        ('U', 'User'),
        ('M', 'Moderator'),
        ('A', 'Admin'),
    ]

    role = models.CharField(
        max_length=1,
        choices=ROLE_CHOICES,
        default='U'
    )

    bio = models.TextField(default='Пусто')

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(
            regex='^[\w.@+-]+\Z',
            message='Недопустимые символы в username',
        ),
        ]
    )


User = get_user_model()


class Category(models.Model):
    """Модель категории."""
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование категории'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Уникальный идентификатор категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class Genre(models.Model):
    """Модель жанра."""
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование жанра'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Уникальный идентификатор жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование произведения'
    )
    year = models.IntegerField(
        verbose_name='Год создания произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class GenreTitle(models.Model):
    """Промежуточная модель для связи произведения и жанра."""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    """Модель отзыва."""
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_and_author'),
        )

    def __str__(self):
        return self.text[:CHAR_OUTPUT_LIMIT]
