from django.db.models import QuerySet
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.models import Guild
from core.serializers import GuildSerializer


class GuildsViewSet(ModelViewSet):
    model = Guild
    serializer_class = GuildSerializer

    def get_queryset(self) -> QuerySet:
        return Guild.objects.all()

    def handshake(self, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
