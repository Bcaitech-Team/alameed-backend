from django.contrib.auth import get_user_model
from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from ..models import ChatMessage, ChatFile, Ticket


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatFile
        fields = "__all__"

    def to_representation(self, value):
        data = super().to_representation(value)
        data["name"] = value.file_name()
        return data


class ChatMessageSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)
    user = UserDetailsSerializer()

    class Meta:
        model = ChatMessage
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'description', 'user', 'status',
                  'status_display', 'created_at', 'updated_at', 'resolved_at']
        read_only_fields = ['user', 'created_at', 'updated_at', 'resolved_at']

    def get_status_display(self, obj):
        return obj.get_status_display()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data["status"] = "open"
        return super().create(validated_data)
