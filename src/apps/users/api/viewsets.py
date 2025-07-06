from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response

from src.apps.users.api.serializers import UserDetailsSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    model = get_user_model()
    queryset = model.objects.all()
    serializer_class = UserDetailsSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name']