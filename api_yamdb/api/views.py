from rest_framework import viewsets

from .serializers import GenreSerializer, TitleSerializer
from reviews.models import Genre, Title


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = ...  # Настройки доступа не настроены.


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = ...  # Настройки доступа не настроены.
