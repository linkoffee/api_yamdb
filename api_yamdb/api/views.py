from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from reviews.models import Category, Genre, MyUser, Title

from .permissions import IsAuthorOrReadOnly, UserRolePermissions, RolePermissions
from .serializers import (CategorySerializer, CustomUserSerializer,
                          GenreSerializer, TitleSerializer)


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


class MyUserViewSet(UserViewSet):
    model = MyUser
    serializer_class = CustomUserSerializer
    lookup_field = 'username'
    permission_classes = [UserRolePermissions,]
    # lookup_field = 'username'  # ещё есть lookup_url_kwarg = 'username'
