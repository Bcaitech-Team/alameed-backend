from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .serializers import (
    VehicleReviewSerializer,
)
from ..models import VehicleReview


class VehicleReviewViewSet( viewsets.ModelViewSet):
    """
    ViewSet for Brand model
    Admin only for write operations
    """
    queryset = VehicleReview.objects.all()
    serializer_class = VehicleReviewSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['vehicle', ]
