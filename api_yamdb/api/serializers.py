from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, MyUser, Review, Title
# PEP8:  Импорты нужно отсортировать в правильном порядке с верху вниз:
#  - импорты из стандартных библиотек
#  - импорты сторонних библиотек (djando, rest_framework и т.д.)
#  - импорты модулей этого проекта
#  Между этими группами импортов должна быть пустая строка.


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
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        scores = Review.objects.filter(title_id=obj).values_list(
            'score',
            flat=True
        )
        if not scores:
            return None
        rating_sum = sum(scores)
        return rating_sum / len(scores)


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
        required=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class CurrentTitleDefault:  # Лишний класс, который еще и делает лишний запрос в БД, не нужно получать произведение.

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

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        request = self.context['request']
        title = get_object_or_404(  # Лишний запрос в БД, получать произведение не нужно. Достаточно в фильтр в 103 строке передать его id.
            Title,
            id=self.context['request'].parser_context['kwargs']['title_id']
        )
        if request.method == 'POST':  # Поднять выше получения id произведения, зачем его получать, если метод будет не пост?
            if Review.objects.filter(author=self.context['request'].user,
                                     title=title).exists():
                raise serializers.ValidationError('Отзыв уже оставлен')
        return attrs


class GetTokenSerializer(serializers.ModelSerializer):
    # Для классов Регистрации и Проверки токена не нужно общение с БД, нужно переопределить родительский класс.
    # Так же смотри замечание в модели про валидацию и про длину полей, это касается всех сериалайзеров для Пользователя.
    """Сериализатор для получения пользователем JWT-токена."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )

    class Meta:
        model = MyUser
        fields = (
            'username',
            'confirmation_code'
        )


class CustomUserSerializer(serializers.ModelSerializer):  # Custom Никогда и нигде не использовать эту приставку, так же как и My, это плохой тон.
    """Сериализатор под нужды администратора."""

    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class NotAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для остальных пользователей."""

    class Meta:  # Нужно наследовать и класс и мету от сериализатора для админа и удалить 146-149 строки.
        model = MyUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""

    class Meta:
        model = MyUser
        fields = ('email', 'username')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if MyUser.objects.filter(username=data.get('username')):
            if not MyUser.objects.filter(email=data.get('email')):
                raise serializers.ValidationError(
                    'Указан неверный email'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели комментариев."""

    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
