from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination


from reviews.models import MyUser
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class RegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    # queryset = Post.objects.all()
    serializer_class = PostSerializer
    """permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )"""

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
