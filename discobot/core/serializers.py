from rest_framework import serializers

from core.models import Movie, Guild, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    already_seen = UserSerializer(read_only=True, many=True)
    want_to_see = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Movie
        fields = '__all__'


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = '__all__'

