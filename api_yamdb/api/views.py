from rest_framework import viewsets

from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from reviews.models import Category, Genre, Title


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = ...  # Настройки доступа не настроены.


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = ...  # Настройки доступа не настроены.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = ...  # Настройки доступа не настроены.
