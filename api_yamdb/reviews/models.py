from django.db import models

from .constants import MAX_NAME_LENGTH, CHAR_OUTPUT_LIMIT


class Title(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = ...  # Здесь пока ничего нет, т.к. нет модели Genre.
    category = ...  # Здесь пока ничего нет, т.к. нет модели Category.

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]
