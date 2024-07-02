from django.db import models

from .constants import MAX_NAME_LENGTH


class Title(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = ...  # Здесь пока ничего нет, т.к. нет модели Genre.
    category = ...  # Здесь пока ничего нет, т.к. нет модели Category.
