from rest_framework import serializers

from core.models import Movie, Guild, User, Ranking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Ranking
        fields = ('movie', 'user', 'rating')


class MovieSerializer(serializers.ModelSerializer):
    already_seen = UserSerializer(read_only=True, many=True)
    want_to_see = UserSerializer(read_only=True, many=True)
    rankings = RatingSerializer(source='movie_rankings', many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = '__all__'
