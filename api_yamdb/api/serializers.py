from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from reviews.models import MyUser


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
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
