from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import CHAR_OUTPUT_LIMIT, MAX_NAME_LENGTH, MAX_SLUG_LENGTH
from .validators import username_validator

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class MyUser(AbstractUser):

    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[
            validators.RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в username',
            ),
            username_validator,
        ]
    )

    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=False,
        default='XXXX'
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('id',)
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


@receiver(post_save, sender=MyUser)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()


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
