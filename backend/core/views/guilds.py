from django.db.models import QuerySet
from rest_framework.viewsets import ModelViewSet

from core.models import Guild
from core.serializers import GuildSerializer


class GuildsViewSet(ModelViewSet):
    model = Guild
    serializer_class = GuildSerializer

    def get_queryset(self) -> QuerySet:
        return Guild.objects.all()
