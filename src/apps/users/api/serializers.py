from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "groups",
            "user_permissions",
        ]
        exclude = ["password"]


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        write_only=True,
        required=True,
    )
    last_name = serializers.CharField(
        write_only=True,
        required=True,
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=get_user_model().objects.all())],
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )


    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    "A user is already registered with this e-mail address."
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            # "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username', 'email']




class AssignPermissionsSerializer(serializers.Serializer):
    # target_type = serializers.ChoiceField(choices=['user', 'group'])
    target_id = serializers.IntegerField()
    permissions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=['add', 'remove'], default='add')

    def validate(self, data):
        # target_type = data['target_type']
        target_type = 'user'  # Assuming we are always dealing with users for simplicity
        target_id = data['target_id']

        # Validate target exists
        if target_type == 'user':
            try:
                get_user_model().objects.get(id=target_id)
            except  get_user_model().DoesNotExist:
                raise serializers.ValidationError("User not found")
        elif target_type == 'group':
            try:
                Group.objects.get(id=target_id)
            except Group.DoesNotExist:
                raise serializers.ValidationError("Group not found")

        return data


class ModelPermissionsSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(choices=['user', 'group'])
    target_id = serializers.IntegerField()
    app_label = serializers.CharField(max_length=100)
    model_name = serializers.CharField(max_length=100)
    permission_types = serializers.ListField(
        child=serializers.ChoiceField(choices=['add', 'change', 'delete', 'view']),
        default=['add', 'change', 'delete', 'view']
    )
    action = serializers.ChoiceField(choices=['add', 'remove'], default='add')

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"

