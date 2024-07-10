from django.utils.text import slugify
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenObtainSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Category, Genre, MyUser, Title


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


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
    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


"""class CustomUserSerializer(UserSerializer):
    username = serializers.SlugRelatedField(
        slug_field='username',
        queryset=MyUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    email = serializers.EmailField()

    class Meta:
        model = MyUser
        fields = '__all__'"""


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('email', 'username')
