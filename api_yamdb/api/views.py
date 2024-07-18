from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import APIUser, Category, Comment, Genre, Review, Title
from .email_func import send_code_to_email
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrStaffPermission,
                          IsAuthorOrModerPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          NotAdminSerializer, ReviewSerializer,
                          SignUpSerializer, TitleSerializerForRead,
                          TitleSerializerForWrite, UserSerializer)


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


class APIUserViewSet(viewsets.ModelViewSet):
    """
    Управляет адресами, начинающимися с users/.
    Права доступа: различаются в зависимости от пользовательских ролей.
    По адресу users/me доступна информация о собственном профиле.
    """

    queryset = APIUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrStaffPermission,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
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
        return Response(serializer.data)


class APISignup(views.APIView):
    """
    Получить код подтверждения на переданный email.
    Права доступа: Доступно без токена.
    Использовать имя 'me' в качестве username запрещено.
    Поля email и username должны быть уникальными.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if not APIUser.objects.filter(
            username=request.data.get('username')
        ).exists():
            serializer = SignUpSerializer(data=request.data)  # <-
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            send_code_to_email(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignUpSerializer(
            get_object_or_404(APIUser, username=request.data.get('username')),
            data=request.data,
            partial=True  # <- я не знаю как указывать это в сериализаторе
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_code_to_email(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class APITokenObtainView(TokenObtainPairView):  # APIView тот же самый
    # только тесты не падают
    """
    Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена.
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # толку-то мне от этих отлично,
        # если вокруг всё непонятно как переделывать
        data = serializer.validated_data
        if not APIUser.objects.filter(  # <- ну не могу перетаскивать,
            # ну тесты падают Key Error
            username=request.data.get('username')
        ).exists():
            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)  # failed 400!=404
        user = APIUser.objects.get(username=data['username'])
        if default_token_generator.check_token(
            user,
            data.get('confirmation_code')
        ):
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
