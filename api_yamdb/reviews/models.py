from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from .constants import (CHAR_OUTPUT_LIMIT, MAX_NAME_LENGTH, MAX_SLUG_LENGTH,
                        ROLE_CHOICES)
from .validators import username_validator


class MyUser(AbstractUser):  # My Никогда и нигде не использовать эту приставку, так же как и Custom, это плохой тон.
    """Модель пользователя."""
    # По PEP257 докстрингс должны заканчиваться точкой, первая строка должна заканчиваться точкой,
    # после докстрингс класса должна быть пустая строка. Исправить везде
    role = models.CharField(
        max_length=9,  # Длину нужно подсчитать прямо тут, подсказка: используем лен и генератор. 
        choices=ROLE_CHOICES,
        default='user',  # Используем константу, никаких литералов быть не должно.
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
        blank=False,  # Это значение по умолчанию, его писать не нужно нигде. Как и 44 строка.
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
        return self.role == ROLE_CHOICES[1][0]  # Зачем, так доставать, есть же константы! Нужно добавить сюда и супер пользователя.

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
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # Отлично!, но лучше добавить еще и сообщения об ошибках. Все магические числа убрать в файл для констант.
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
    # Оба класса (Ревью и Комменты) имеют одинаковые поля и в мете тоже, значит можно создать базовый абстрактный класс и унаследовать от него обе модели.
    # Но не забудьте что мету тоже нужно наследовать иначе она перезапишет всё, а не только то что 'другое'. Класс наследуется от класса, мета от меты.
    # Еще в моделях ревью и комментов можно в мете добавить умолчательное значение related_name, чтобы не указывать его для каждого поля.
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
