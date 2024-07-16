from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
from .mixins import CategoryGenreMixin


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset модели произведения."""

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


class GenreViewSet(CategoryGenreMixin):
    """Viewset модели жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreMixin):
    """Viewset модели категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset модели отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_title(self):
        """Получаем произведение для отзыва."""
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        """Получаем отзывы к конкретному произведению."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Добавляем авторизованного пользователя к отзыву."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


# My Никогда и нигде не использовать эту приставку, так же как и Custom, это плохой тон.
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
        # Лишний метод post, админ сделает свои дела по нику, а не в me. Так же и условие в 123 строке лишнее.
        methods=['GET', 'PATCH', 'POST'],
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


class SignupViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    # Избыточный родитель, тут достаточно APIView, либо вообще функции с декоратором apiview.
    # Тоже и для токена.
    # Так же в обоих этих классах должно быть всего 4 строки:
    # - передать в сериализатор данные
    # - проверить валидность
    # - записать
    # - вернуть Response
    # Всё остальное (создание и валидация) должно быть в сериализаторе.
    """
    Получить код подтверждения на переданный email. Права доступа: Доступно без
    токена. Использовать имя 'me' в качестве username запрещено. Поля email и
    username должны быть уникальными.
    """

    queryset = MyUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    # Это тут всё зачем? Есть же функция для отправки, в файле utils.
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
        if not MyUser.objects.filter(
            username=request.data.get('username')
        ).exists():
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)  # ОТЛИЧНО!
            user = serializer.save()
            confirmation_code = default_token_generator.make_token(user)
            self.send_email(user.username, confirmation_code, user.email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignUpSerializer(
            get_object_or_404(MyUser, username=request.data.get('username')),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        self.send_email(user.username, confirmation_code, user.email)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyTokenObtainView(TokenObtainPairView):
    """
    Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена.
    """

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not MyUser.objects.filter(
            username=request.data.get('username')
        ).exists():
            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)
        user = MyUser.objects.get(username=data['username'])
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
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerPermission,)

    def get_review(self):
        """Получаем отзыв для комментария."""
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        """Получаем комментарии к конкретному отзыву."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Присваиваем автора комментарию."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
