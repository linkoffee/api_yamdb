from rest_framework import serializers

from reviews.models import APIUser, Category, Comment, Genre, Review, Title


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
        max_length=150,  # Все настройки длины выносим в файл с константами (не settings), для многих полей они будут одинаковыми, не повторяемся.
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )

    class Meta:
        model = APIUser
        fields = (
            'username',
            'confirmation_code'
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор под нужды администратора."""

    class Meta:
        model = APIUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class NotAdminSerializer(UserSerializer):
    """Сериализатор для остальных пользователей."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


# валятся тесты с serializers.Serializer
class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""

    class Meta:
        model = APIUser
        fields = ('email', 'username')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if APIUser.objects.filter(username=data.get('username')):
            if not APIUser.objects.filter(email=data.get('email')):
                raise serializers.ValidationError(
                    'Указан неверный email'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор данных для модели комментариев."""

    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
