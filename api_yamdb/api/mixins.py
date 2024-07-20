from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination


from .permissions import IsAdminOrReadOnly


class CategoryGenreMixin(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Миксин для вьюсета категории и жанра."""

    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
