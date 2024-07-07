from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from reviews.models import MyUser

from djoser.serializers import UserSerializer
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer
)


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели отзывов."""

    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):  # не готово
    username = serializers.SlugRelatedField(
        slug_field='username',
        queryset=MyUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    email = serializers.EmailField()

    class Meta:
        fields = ('email', 'username', 'id')
        model = MyUser
        validators = [
            UniqueTogetherValidator(
                queryset=MyUser.objects.all(),
                fields=('username', 'email'),
                message='Такой профиль уже есть'
            )
        ]

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.name
        # ...

        return token

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        return data


class CustomUserSerializer(UserSerializer):
    username = serializers.SlugRelatedField(
        slug_field='username',
        queryset=MyUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    email = serializers.EmailField()

    class Meta:
        model = MyUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'role',
            'bio'
        )

    def validate(self, data):
        if len(data['username']) or len(data['first_name']) > 150:
            raise serializers.ValidationError('name too long')
        return data
