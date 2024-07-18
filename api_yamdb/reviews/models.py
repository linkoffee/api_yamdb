from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from .constants import (CHAR_OUTPUT_LIMIT, MAX_NAME_LENGTH, MAX_SCORE,
                        MAX_SLUG_LENGTH, MIN_SCORE, MIN_YEAR, CURRENT_YEAR,
                        ROLE_CHOICES)
from .validators import username_validator


# My Никогда и нигде не использовать эту приставку, так же как и Custom, это плохой тон.
class MyUser(AbstractUser):
    """Модель пользователя."""
    # По PEP257 докстрингс должны заканчиваться точкой, первая строка должна заканчиваться точкой,
    # после докстрингс класса должна быть пустая строка. Исправить везде
    role = models.CharField(
        # Длину нужно подсчитать прямо тут, подсказка: используем лен и генератор.
        max_length=9,
        choices=ROLE_CHOICES,
        # Используем константу, никаких литералов быть не должно.
        default='user',
        verbose_name='Роль'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    email = models.EmailField(
        max_length=254,
        # Общее для всех моделей:
        # Смотрим редок внимательно и видим там правильное ограничение длинны для всех полей.
        # Все настройки длины выносим в файл с константами (не settings), для многих полей они будут одинаковыми, не повторяемся.
        # Для всех полей нужны verbose_name.
        # Для всех классов нужны в классах Meta verbose_name и verbose_name_plural.
        # У всех классов где используется пагинация, должна быть умолчательная сортировка.
        # Для всех классов нужны методы __str__.
        unique=True,
        verbose_name='Электронная почта'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        # Это значение по умолчанию, его писать не нужно нигде. Как и 44 строка.
        blank=False,
        null=False,
        validators=[
            # Лучше написать свой валидатор с проверкой на me и на регулярку,
            # штатный не ответит на вопрос, какой неверный символ ввел пользователь,
            # только укажет на ошибку, пользователю придется гадать, какой из символов неверный,
            # нужно дать четкий ответ, какой символ недопустим в имени, рекомендую использовать re.sub,
            # получить строку из запрещенных символов, проверить, что она есть, выдать ошибку с текстом.
            # Можно лучше(Необязательно к выполнению):
            # Валидатор для username можно использовать в миксине вот так:

            # ИмяМиксина:
            #   def validate_username(self, username):
            #       return имя_метода_валидации(username)

            # И наследовать сериалайзеры от этого миксина так:
            # Сериалайзер(ОсновнойРодитель, Миксин)
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в username',
            ),
            username_validator,
        ]
    )

    @property
    def is_user(self):  # Негде не используется.
        return self.role == ROLE_CHOICES[0][0]

    @property  # ОТЛИЧНО!
    def is_admin(self):
        # Зачем, так доставать, есть же константы! Нужно добавить сюда и супер пользователя.
        return self.role == ROLE_CHOICES[1][0]

    @property
    def is_moderator(self):
        return self.role == ROLE_CHOICES[2][0]

    class Meta:
        ordering = ('id',)
        # Никакого прока от сортировки по техническому полю "ключ" нет.
        # Учти, что значения ключей - это случайные величины (точнее они могут непредсказуемо измениться).
        # Поэтому сортировка по ним - это опять случайная последовательность объектов.
        # Лучше заменить на предметное поле (можно на несколько полей - ведь это перечисление)
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


User = get_user_model()  # Поднять под импорты.


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
        User,
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
