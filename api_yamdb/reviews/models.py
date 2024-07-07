from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

from .constants import CHAR_OUTPUT_LIMIT, MAX_NAME_LENGTH, MAX_SLUG_LENGTH


class Category(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH)

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class Genre(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH)

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class Title(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, related_name='titles'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='titles'
    )

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]


class MyUser(AbstractUser):
    ROLE_CHOICES = [
        ('U', 'User'),
        ('M', 'Moderator'),
        ('A', 'Admin'),
    ]

    role = models.CharField(
        max_length=1,
        choices=ROLE_CHOICES,
        default='User'   # было 'U' и я не делал миграции
        # один чел в базе до сих пор с ролью 'U'
    )

    bio = models.TextField(default='Пусто')
    email = models.EmailField(blank=False, unique=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Недопустимые символы в username',
        ),
        ]
    )
