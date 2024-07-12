from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Comment, Genre, MyUser, Review, Title
from .permissions import (IsAdminOrStaffPermission, IsAdminOrReadOnly,
                          IsUserForSelfPermission, IsAuthorOrModerPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          CustomUserSerializer, GenreSerializer,
                          GetTokenSerializer, NotAdminSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleSerializerForRead, TitleSerializerForWrite,)
from .filters import TitleFilter


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset модели произведения."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleSerializerForWrite
        return TitleSerializerForRead


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Viewset модели жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Viewset модели категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset модели отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_queryset(self):
        """Получаем отзывы к конкретному произведению."""
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        """Добавляем авторизованного пользователя к отзыву."""
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class MyUserViewSet(viewsets.ModelViewSet):
    """
    Управляет адресами, начинающимися с users/. Права доступа:
    различаются в зависимости от пользовательских ролей.
    По адресу users/me доступна информация о собственном профиле.
    """

    queryset = MyUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminOrStaffPermission,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH', 'POST',],
        detail=False,
        permission_classes=(IsUserForSelfPermission, IsAuthenticated),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = CustomUserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = CustomUserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class APISignup(APIView):
    """
    Получить код подтверждения на переданный email. Права доступа: Доступно без
    токена. Использовать имя 'me' в качестве username запрещено. Поля email и
    username должны быть уникальными.
    """

    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(username, confirmation_code, email):
        email = EmailMessage(
            subject='Код подтвержения для доступа к API!',
            body=(
                    f'Доброе время суток, {username}.'
                    '\nКод подтвержения для доступа к API:'
                    f'\n{confirmation_code}'
            ),
            to=(email,)
        )
        email.send()

    def post(self, request):
        username = request.data.get('username')
        if not MyUser.objects.filter(username=username).exists():
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['username'] != 'me':
                user = serializer.save()
                self.send_email(
                    user.username, user.confirmation_code, user.email)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                'Username указан невено!', status=status.HTTP_400_BAD_REQUEST
            )
        user = get_object_or_404(MyUser, username=username)
        serializer = SignUpSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['email'] == user.email:
            user = serializer.save()
            self.send_email(user.username, user.confirmation_code, user.email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            'Почта указана неверно!', status=status.HTTP_400_BAD_REQUEST
        )


class MyTokenObtainView(TokenObtainPairView):
    """
    Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена.
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = MyUser.objects.get(username=data['username'])
        except MyUser.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset модели комментариев."""

    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_queryset(self):
        """Получаем комментарии к конкретному отзыву."""
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        """Присваиваем автора комментарию."""
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
