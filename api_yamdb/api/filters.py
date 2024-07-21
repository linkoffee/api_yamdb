from django_filters import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """
    Фильтр для произведений.

    Фильтрует произведения по уникальному значению категории,
    Уникальному значению жанра, названию и году выхода.
    """

    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
