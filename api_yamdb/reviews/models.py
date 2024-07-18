from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,)
from django.db import models

from .constants import (ADMIN, CHAR_OUTPUT_LIMIT, EMAIL_LENGTH,
                        MAX_NAME_LENGTH, MAX_SLUG_LENGTH, MODERATOR,
                        ROLE_CHOICES, USER, USERNAME_LENGTH)
from .validators import username_validator


class APIUser(AbstractUser):
    """Модель пользователя."""

    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта'
    )

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        blank=False,
        null=False,
        validators=[username_validator,]
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('username', 'id',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return self.username


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

    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='reviews',
        verbose_name='Наименование произведения'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return self.text[:CHAR_OUTPUT_LIMIT]


class Comment(models.Model):
    """Модель комментария."""

    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:CHAR_OUTPUT_LIMIT]
