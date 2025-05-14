from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import ChatMessageSerializer, FileSerializer, TicketSerializer, ContactMessageSerializer
from ..models import ChatMessage, ChatFile, Ticket, ContactMessage


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    Class representing a support messages viewset
    """

    serializer_class = ChatMessageSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["date"]
    filterset_fields = [
        "user__username",
        "date",
        "room__id",
    ]
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return ChatMessage.objects.all()


class FileViewSet(viewsets.ModelViewSet):
    """
    Class representing a support media viewset
    """

    serializer_class = FileSerializer
    http_method_names = ["get", "head", "options", "post"]
    queryset = ChatFile.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'updated_at', 'resolved_at']

    def get_queryset(self):
        # Regular users can only see their own tickets
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.resolve()
        return Response({'status': 'ticket resolved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'closed'
        ticket.save()
        return Response({'status': 'ticket closed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = 'open'
        ticket.resolved_at = None
        ticket.save()
        return Response({'status': 'ticket reopened'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        ticket = self.get_object()
        messages = ChatMessage.objects.filter(room=ticket)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class HeartbeatViewSet(viewsets.ViewSet):
    """
    Class representing a heartbeat viewset
    """
    http_method_names = ["get", "head", "options"]

    def list(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    Class representing a contact messages viewset
    """

    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.all()
    permission_classes = [permissions.AllowAny]
