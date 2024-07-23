from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, permissions, status, views,
                            viewsets, mixins)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrStaffPermission,
                          IsAuthorOrModerPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          NotAdminSerializer, ReviewSerializer,
                          SignUpSerializer, TitleSerializerForRead,
                          TitleSerializerForWrite, UserSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet модели произведения."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ('id', 'name', 'year')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializerForWrite
        return TitleSerializerForRead


class CategoryGenreViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Базовый ViewSet для категории и жанра."""

    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(CategoryGenreViewSet):
    """ViewSet модели жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreViewSet):
    """ViewSet модели категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet модели отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_title(self):
        """Получаем произведение для отзыва."""
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        """Получаем отзывы к конкретному произведению."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Добавляем авторизованного пользователя к отзыву."""
        serializer.save(author=self.request.user, title=self.get_title())


class APIUserViewSet(viewsets.ModelViewSet):
    """
    Управляет адресами, начинающимися с users/.
    Права доступа: различаются в зависимости от пользовательских ролей.
    По адресу users/me доступна информация о собственном профиле.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrStaffPermission,)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @get_current_user_info.mapping.patch
    def update_user_info(self, request):
        if request.user.is_admin:
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)
        serializer = NotAdminSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class APISignup(views.APIView):
    """
    Получить код подтверждения на переданный email.
    Права доступа: Доступно без токена.
    Использовать имя 'me' в качестве username запрещено.
    Поля email и username должны быть уникальными.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class APITokenObtainView(views.APIView):
    """
    Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Повторю еще раз, тут должно быть 4 строки, см. выше.
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({"token": token}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset модели комментариев."""

    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_review(self):
        """Получаем отзыв для комментария."""
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        """Получаем комментарии к конкретному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Присваиваем автора комментарию."""
        serializer.save(author=self.request.user, review=self.get_review())
