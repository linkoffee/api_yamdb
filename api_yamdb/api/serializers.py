from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, MyUser, Review, Title


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

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializerForWrite(serializers.ModelSerializer):
    """Сериализатор данных модели произведения для записи."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'

class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        title_id = serializer_field.context['view'].kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def __repr__(self):
        return '%s()' % self.__class__.__name__

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели отзывов."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    # title = serializers.HiddenField(default=CurrentTitleDefault())
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=('author', 'id')
        #     )
        # ]
    def validate(self, attrs):
        request = self.context['request']
        title = get_object_or_404(
            Title,
            id=self.context['request'].parser_context['kwargs']['title_id']
        )
        if request.method == 'POST':
            if Review.objects.filter(author=self.context['request'].user,
                                     title=title).exists():
                raise serializers.ValidationError('Отзыв уже оставлен')
        return attrs

class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

    class Meta:
        model = MyUser
        fields = (
            'username',
            'confirmation_code'
        )


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


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


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели комментариев."""
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')
    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)

