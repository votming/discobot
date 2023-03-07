from django.db.models import QuerySet
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.models import ChatLog, Fact
from core.serializers import ChatLogSerializer, FactSerializer


class ChatLogViewSet(ModelViewSet):
    model = ChatLog
    serializer_class = ChatLogSerializer

    def get_queryset(self) -> QuerySet:
        return ChatLog.objects.all()


class FactViewSet(ModelViewSet):
    model = Fact
    serializer_class = FactSerializer

    def get_queryset(self) -> QuerySet:
        return Fact.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
