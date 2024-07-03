from rest_framework import serializers

from reviews.models import Genre, Title


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        field = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        field = '__all__'
