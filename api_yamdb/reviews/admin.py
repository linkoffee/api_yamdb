from django.contrib import admin

from .models import Genre, Title

admin.site.empty_value_display = 'Здесь пока ничего нет:('


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'genre',
        'category',
    )
    list_editable = (
        'description',
    )
    search_fields = (
        'title',
        'year',
        'genre',
        'category',
    )
    list_filter = (
        'title',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_editable = (
        'name',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
    )
