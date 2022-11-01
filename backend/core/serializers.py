from rest_framework import serializers

from core.models import Movie, Guild, User, Ranking, Session



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
    dont_want_to_watch = UserSerializer(read_only=True, many=True)
    rankings = RatingSerializer(source='movie_rankings', many=True, read_only=True)
    sessions = serializers.PrimaryKeyRelatedField(source='session_set', many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    audience = UserSerializer(many=True)
    available_movies = MovieSerializer(many=True)
    audience_want_to_see_movies = MovieSerializer(many=True)
    club_has_seen = MovieSerializer(many=True)
    seen_at = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Session
        fields = ['id', 'guild', 'movie', 'club_has_seen', 'available_movies', 'audience_want_to_see_movies', 'seen_at', 'audience', 'created_at', 'updated_at']
