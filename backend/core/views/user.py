from django.db.models import QuerySet
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.models import ChatLog, Fact, User
from core.serializers import ChatLogSerializer, FactSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet:
        return User.objects.all()

    def get_facts(self, request, *args, **kwargs):
        facts = Fact.objects.filter(chat_log__user__id=kwargs['pk']).order_by('id')
        serializer = FactSerializer(facts, many=True)
        return Response(serializer.data)
