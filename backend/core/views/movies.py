from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import json

from core.models import Movie, User
from core.serializers import MovieSerializer, UserSerializer


class MoviesViewSet(ModelViewSet):
    model = Movie
    serializer_class = MovieSerializer

    def get_queryset(self) -> QuerySet:
        return Movie.objects.all()

    def _validate_user(self, id, data):
        qs = User.objects.filter(pk=id)
        if not qs.exists():
            user = UserSerializer(data=data)
            user.is_valid(raise_exception=True)
            user.save()
        else:
            qs.update(**data)
        user = User.objects.filter(pk=data['id']).first()
        return user

    def rate_movie(self, request, *args, **kwargs):
        data = json.loads(request.data)
        movie = Movie.objects.get(uuid=data['uuid'], guild_id=data['guild_id'])
        user = self._validate_user(data['user']['id'], data['user'])
        movie.rankings.remove(user)
        movie.rankings.add(user, through_defaults={'rating': data['rating']})
        if not movie.already_seen.all().filter(id=user.id).exists():
            movie.want_to_see.remove(user)
            movie.already_seen.add(user)
        print(f'rating: {data["rating"]}, user: {user}')
        return Response('ok')

    def set_watched(self, request, *args, **kwargs):
        data = json.loads(request.data)
        movie = Movie.objects.get(uuid=data['uuid'])
        user = self._validate_user(data['user']['id'], data['user'])

        movie.already_seen.add(user)
        movie.want_to_see.remove(user)
        print(f'want to see: {list(movie.already_seen.all())}')
        return Response('ok')

    def set_unwatched(self, request, *args, **kwargs):
        data = json.loads(request.data)
        movie = Movie.objects.get(uuid=data['uuid'])
        user = self._validate_user(data['user']['id'], data['user'])

        movie.already_seen.remove(user)
        movie.want_to_see.remove(user)
        return Response('ok')

    def subscribe_to_watch(self, request, *args, **kwargs):
        data = json.loads(request.data)
        movie = Movie.objects.get(uuid=data['uuid'], guild_id=data['guild_id'])
        user = self._validate_user(data['user']['id'], data['user'])

        movie.want_to_see.add(user)
        movie.already_seen.remove(user)
        print(f'want to see: {list(movie.want_to_see.all())}')
        return Response('ok')

    def get_movie(self, request, *args, **kwargs):
        data = json.loads(request.data)
        movie = Movie.objects.filter(**data).first()
        if movie:
            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)