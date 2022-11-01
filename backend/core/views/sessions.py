from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import json
import random

from core.models import Movie, User, Session
from core.serializers import MovieSerializer, UserSerializer, SessionSerializer


class SessionsViewSet(ModelViewSet):
    model = Session
    serializer_class = SessionSerializer
    guild_id = None

    def get_queryset(self) -> QuerySet:
        if self.guild_id:
            return Session.objects.filter(guild_id=self.guild_id).exclude(seen_at=None).order_by('-seen_at')
        return Session.objects.all()

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

    def list(self, request, *args, **kwargs):
        self.guild_id = kwargs.get('guild_id', None)
        return super().list(self, request, *args, **kwargs)

    def join_session(self, request, *args, **kwargs):
        session = self.get_object()
        if session.seen_at:
            return Response(status=400)
        data = json.loads(request.data)
        user = self._validate_user(data['id'], data)
        session.audience.add(user)
        return Response()

    def leave_session(self, request, *args, **kwargs):
        session = self.get_object()
        if session.seen_at:
            return Response(status=400)
        data = json.loads(request.data)
        user = self._validate_user(data['id'], data)
        session.audience.remove(user)
        return Response()

    def finish_session(self, request, *args, **kwargs):
        session = self.get_object()
        if session.movie:
            session.seen_at = timezone.now()
            session.save()
            movie = session.movie
            for user in session.audience.all():
                movie.want_to_see.remove(user)
                try:
                    movie.already_seen.add(user)
                except Exception as e:
                    print(str(e))
                    pass
            return Response()
        else:
            return Response(status=400)

    def select_random(self, request, *args, **kwargs):
        session = self.get_object()
        if session.seen_at:
            return Response(status=400)
        movie = random.choice(session.available_movies)
        session.movie = movie
        session.save()
        return Response()

    def select_movie(self, request, *args, **kwargs):
        session = self.get_object()
        if session.seen_at:
            return Response(status=400)
        data = json.loads(request.data)
        movie = Movie.objects.filter(name=data['title']).first()
        if movie:
            session.movie = movie
            session.save()
            return Response()
        return Response(status=400)

    def decline_movie(self, request, *args, **kwargs):
        session = self.get_object()
        session.movie = None
        session.save()
        return Response()

    def create(self, request, *args, **kwargs):
        #super().create(request, *args, **kwargs)
        guild_id = request.data.get('guild_id', None)
        members_ids = request.data.get('members_ids', None)
        if guild_id:
            session = Session.objects.filter(guild_id=guild_id, seen_at=None)
            if session.exists():
                session = session.first()
            else:
                session = Session.objects.create(guild_id=guild_id)
            if members_ids:
                session.load_top_movies(members_ids)
            serializer = SessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=400)
