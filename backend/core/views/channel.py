from django.db.models import QuerySet
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.models import Guild, Channel
from core.serializers import GuildSerializer, ChannelSerializer


class ChannelViewSet(ModelViewSet):
    model = Channel
    serializer_class = ChannelSerializer

    def get_queryset(self) -> QuerySet:
        return Channel.objects.all()

    def update_config(self, request, *args, **kwargs):
        x=1