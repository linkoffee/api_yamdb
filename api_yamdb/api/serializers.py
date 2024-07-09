from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User

from .utils import CurrentTitleDefault


# class RatingSerializer(serializers.Field):
#
#     def to_representation(self, value):
#         rating_sum = 0
#         for item in value.items:
#             rating_sum += item.rating
#         return rating_sum / len(value.items)
#
#     def to_internal_value(self, data):
#         return data

    # def calculate_rating(self, obj):
    #     rating_sum = 0
    #     for item in obj.items:
    #         rating_sum += item.rating
    #     return rating_sum / len(obj.items)
    #
    # def create(self, validated_data):
    #     # Здесь вы можете создать новый объект OtherModel с вычисленным рейтингом
    #     return super().create(validated_data)
    #
    # def update(self, instance, validated_data):
    #     # Здесь вы можете обновить существующий объект OtherModel с вычисленным рейтингом
    #     return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')


class ReadTitleSerializer(serializers.ModelSerializer):
    # rating = serializers.IntegerField(read_only=True)
    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating',)

    # def get_rating(self, obj):
    #     scores = Review.objects.filter(title_id=obj.id).values('score',)
    #     rating_sum = 0
    #     print(scores, '!!!!!!!!!!!!!!')
    #     for score in scores:
    #         rating_sum += score
    #     return rating_sum / len(scores)
    def get_rating(self, obj):
        scores = Review.objects.filter(title_id=obj).values_list('score',
                                                                    flat=True)
        if not scores:
            return None
        rating_sum = sum(scores)
        return rating_sum / len(scores)




class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    title = serializers.HiddenField(
        default=CurrentTitleDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]

    def validate(self, data):
        if not 1 <= data['score'] <= 10:
            raise serializers.ValidationError(
                'Оценка может быть от 1 до 10!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Username указан неверно!')
        return data


class AuthSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=50)



