from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, MyUser, Review, Title

admin.site.empty_value_display = 'Здесь пока ничего нет:('


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админ панель произведений."""

    list_display = (
        'name',
        'year',
        'description',
        'category',
        'get_genres',
    )
    list_editable = (
        'description',
    )
    search_fields = (
        'name',
        'year',
        'category',
    )
    list_filter = (
        'name',
    )

    @admin.display(description='Жанры произведения')
    def get_genres(self, obj):
        """Получает все жанры через запятую."""
        return ', '.join([genre.name for genre in obj.genre.all()])


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ панель категорий."""

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
    """Админ панель жанров."""

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


"""Админ панель пользователя."""
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('role',)}),
)
admin.site.register(MyUser, UserAdmin)
#  Роль должна быть редактируемой в листе пользователей.


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ панель отзывов."""

    list_display = (
        'title',
        'text',
        'score',
        'author',
        'pub_date'
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'title',
        'score',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ панель комментариев."""

    list_display = (
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = (
        'review',
    )
    list_filter = (
        'review',
        'author',
    )
