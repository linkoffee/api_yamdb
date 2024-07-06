from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination


from reviews.models import MyUser
from .serializers import (CustomUserSerializer)


class MyUserViewSet(UserViewSet):
    model = MyUser
    serializer_class = CustomUserSerializer
