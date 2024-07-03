from rest_framework import viewsets

from .serializers import TitleSerializer
from reviews.models import Title


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = ...  # Настройки доступа не настроены.
