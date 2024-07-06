from .models import MyUser
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Category, Genre, Title

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
        'name',
        'year',
        'genre',
        'category',
    )
    list_filter = (
        'name',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
    )
    list_display_links = (
        'name',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
    )
    list_display_links = (
        'name',
    )


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('role',)}),
)
admin.site.register(MyUser, UserAdmin)
