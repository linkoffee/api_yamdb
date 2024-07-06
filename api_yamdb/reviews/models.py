from django.db import models

from .constants import MAX_NAME_LENGTH, MAX_SLUG_LENGTH, CHAR_OUTPUT_LIMIT

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


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
        default='U'
    )

    bio = models.TextField(default='Пусто')

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(
            regex='^[\w.@+ -]+\Z',
            message='Недопустимые символы в username',
        ),
        ]
    )
