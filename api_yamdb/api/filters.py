from django_filters import FilterSet, CharFilter, NumberFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """
    Фильтрует произведения.
        - по уникальному значению категории(slug)
        - по уникальному значению жанра(slug)
        - по имени
        - по году выхода
    """

    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'year', 'name')
