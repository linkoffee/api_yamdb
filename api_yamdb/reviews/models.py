from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


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
