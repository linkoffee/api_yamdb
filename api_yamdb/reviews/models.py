from django.db import models

from .constants import MAX_NAME_LENGTH, MAX_SLUG_LENGTH, CHAR_OUTPUT_LIMIT


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


class Review(models.Model):
    text = models.TextField()
    # author = models.ForeignKey(
    #     User, on_delete=models.CASCADE, related_name='reviews'
    # )
    author = models.IntegerField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_and_author'),
        )

    def __str__(self):
        return self.text[:CHAR_OUTPUT_LIMIT]
