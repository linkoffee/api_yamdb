from django.db import models

from .constants import MAX_NAME_LENGTH, MAX_SLUG_LENGTH, CHAR_OUTPUT_LIMIT


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
    category = ...  # Здесь пока ничего нет, т.к. нет модели Category.

    def __str__(self):
        return self.name[:CHAR_OUTPUT_LIMIT]
