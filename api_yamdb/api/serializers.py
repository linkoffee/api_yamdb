from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from reviews.constants import EMAIL_LENGTH, USER, USERNAME_LENGTH
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import username_validator
from .email_func import send_code_to_email


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор данных модели категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializerForRead(serializers.ModelSerializer):
    """Сериализатор данных модели произведения для чтения."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializerForWrite(serializers.ModelSerializer):
    """Сериализатор данных модели произведения для записи."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        serializer = TitleSerializerForRead(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели отзывов."""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            if Review.objects.filter(
                    author=self.context['request'].user,
                    title=self.context['request'].parser_context['kwargs']
                    ['title_id']
            ).exists():
                raise serializers.ValidationError('Отзыв уже оставлен')
        return attrs


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения пользователем JWT-токена."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=USERNAME_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True
    )

    def validate(self, data):
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(
            user,
            data.get('confirmation_code')
        ):
            raise serializers.ValidationError('Неверный код')
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        user.is_active = True
        user.save()
        return str(RefreshToken.for_user(user).access_token)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор под нужды администратора."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class NotAdminSerializer(UserSerializer):
    """Сериализатор для остальных пользователей."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        validators=[
            username_validator,
        ],
    )
    email = serializers.EmailField(
        max_length=EMAIL_LENGTH,
    )

    def validate(self, data):
        try:
            User.objects.get_or_create(
                username=data.get('username'),
                email=data.get('email')
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'Такой пользователь уже существует'
            )
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            email=email,
            defaults={'role': USER}
        )
        user.save()

        send_code_to_email(user)
        return user


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор данных для модели комментариев."""

    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
