from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response

from src.apps.users.api.serializers import UserDetailsSerializer, PermissionsSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .serializers import AssignPermissionsSerializer, ModelPermissionsSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    model = get_user_model()
    queryset = model.objects.all()
    serializer_class = UserDetailsSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name']




class AssignPermissionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignPermissionsSerializer

    def post(self, request):
        """
        Assign or remove permissions to/from users or groups

        Request body:
        {
            "target_type": "user",  // or "group"
            "target_id": 1,
            "permissions": ["add_post", "change_post", "delete_post"],
            "action": "add"  // or "remove"
        }
        """
        serializer = AssignPermissionsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        target_id = data['target_id']
        permissions = data['permissions']
        action = data['action']

        # Get target object
        target = get_user_model().objects.get(id=target_id)


        # Process permissions
        assigned_permissions = []
        failed_permissions = []

        for perms in permissions:
            try:
                permission = Permission.objects.get(id=perms)

                if action == 'add':
                    target.user_permissions.add(permission)
                elif action == 'remove':
                    target.user_permissions.remove(permission)

                assigned_permissions.append(perms)

            except Permission.DoesNotExist:pass

        return Response({
            "message": f"Permissions {action}ed successfully",
            "target_id": target_id,
            "assigned_permissions": assigned_permissions,
        }, status=status.HTTP_200_OK)


class ModelPermissionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ModelPermissionsSerializer

    def post(self, request):
        """
        Assign model-specific permissions

        Request body:
        {
            "target_type": "user",
            "target_id": 1,
            "app_label": "blog",
            "model_name": "post",
            "permission_types": ["add", "change", "delete", "view"],
            "action": "add"
        }
        """
        serializer = ModelPermissionsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        target_type = data['target_type']
        target_id = data['target_id']
        app_label = data['app_label']
        model_name = data['model_name']
        permission_types = data['permission_types']
        action = data['action']

        # Get target object
        if target_type == 'user':
            target = User.objects.get(id=target_id)
        else:
            target = Group.objects.get(id=target_id)

        try:
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=model_name
            )
        except ContentType.DoesNotExist:
            return Response(
                {"error": f"Model {app_label}.{model_name} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        assigned_permissions = []
        failed_permissions = []

        for perm_type in permission_types:
            codename = f"{perm_type}_{model_name}"

            try:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type
                )

                if action == 'add':
                    if target_type == 'user':
                        target.user_permissions.add(permission)
                    else:
                        target.permissions.add(permission)
                elif action == 'remove':
                    if target_type == 'user':
                        target.user_permissions.remove(permission)
                    else:
                        target.permissions.remove(permission)

                assigned_permissions.append(codename)

            except Permission.DoesNotExist:
                failed_permissions.append(codename)

        return Response({
            "message": f"Model permissions {action}ed successfully",
            "target_type": target_type,
            "target_id": target_id,
            "model": f"{app_label}.{model_name}",
            "assigned_permissions": assigned_permissions,
            "failed_permissions": failed_permissions
        }, status=status.HTTP_200_OK)


class PermissionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing all permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type__app_label', 'content_type__model', 'codename']

class UserPermissionsViewSet(APIView):
    """
    ViewSet for listing permissions of a specific user.
    """
    serializer_class = PermissionsSerializer
    permission_classes = [permissions.IsAuthenticated]



    def get(self,request, *args, **kwargs):
        return Response({
            "user_permissions": request.user.get_all_permissions(),
        })

