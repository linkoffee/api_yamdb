from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,)
from django.db import models

from .constants import (ADMIN, CHAR_OUTPUT_LIMIT, EMAIL_LENGTH,
                        MAX_NAME_LENGTH, MAX_SLUG_LENGTH, MODERATOR,
                        ROLE_CHOICES, USER, USERNAME_LENGTH)
from .constants import (CHAR_OUTPUT_LIMIT, MAX_NAME_LENGTH, MAX_SCORE,
                        MAX_SLUG_LENGTH, MIN_SCORE, MIN_YEAR, CURRENT_YEAR,
                        ROLE_CHOICES)
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


class BaseCategoryGenreModel(models.Model):
    """Абстрактная модель для категории и жанра."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Уникальный идентификатор'
    )

    class Meta:
        abstract = True
        ordering = ('name',)
        verbose_name = 'Наименование'
        verbose_name_plural = 'Наименования'

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class Category(BaseCategoryGenreModel):
    """Модель категории."""

    class Meta(BaseCategoryGenreModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenreModel):
    """Модель жанра."""

    class Meta(BaseCategoryGenreModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование произведения'
    )
    year = models.SmallIntegerField(
        validators=(
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(CURRENT_YEAR)
        ),
        db_index=True,
        verbose_name='Год создания произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категория произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class BaseReviewCommentModel(models.Model):
    """Базовый класс моделей отзыва и комментария."""

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        APIUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:CHAR_OUTPUT_LIMIT]


class Review(BaseReviewCommentModel):
    """Модель отзыва."""

    score = models.IntegerField(
        validators=[
            MinValueValidator(MIN_SCORE, 'Оценка не может быть меньше 1'),
            MaxValueValidator(MAX_SCORE, 'Оценка не может быть больше 10')
        ],
        verbose_name='Оценка'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name='Наименование произведения'
    )

    class Meta(BaseReviewCommentModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        default_related_name = 'reviews'


class Comment(BaseReviewCommentModel):
    """Модель комментария."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(BaseReviewCommentModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
