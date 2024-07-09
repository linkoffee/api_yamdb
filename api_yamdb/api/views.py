from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from reviews.models import Category, Genre, MyUser, Title, Review, User


from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from .serializers import (CategorySerializer, GenreSerializer,
                          CustomUserSerializer, TitleSerializer,
                          ReviewSerializer)
# from .permissions import IsAdminOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    # permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    # permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    # permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        """Получаем отзывы к конкретному произведению."""
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        """Добавляем авторизованного пользователя к отзыву."""
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class MyUserViewSet(UserViewSet):
    model = MyUser
    serializer_class = CustomUserSerializer
