from django.urls import path

from src.apps.users.api.viewsets import ModelPermissionsAPIView, AssignPermissionsAPIView, UserPermissionsViewSet

urlpatterns = [
    path('assign-permissions/', AssignPermissionsAPIView.as_view(), name='assign_permissions'),
    path('assign-model-permissions/', ModelPermissionsAPIView.as_view(), name='assign_model_permissions'),
path('user-permissions/', UserPermissionsViewSet.as_view(), name='user-permissions')

    # Function-based view alternative

]