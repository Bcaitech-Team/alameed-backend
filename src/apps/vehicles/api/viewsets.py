from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import AdminOnlyMixin
from .serializers import (
    BrandSerializer,
    VehicleTypeSerializer,
    FeatureSerializer,
    VehicleListSerializer,
    VehicleDetailSerializer,
    VehicleCreateUpdateSerializer,
    VehicleImageSerializer,
    InquiryDataSerializer, FavoriteVehicleSerializer, VehiclePriceSerializer, VehiclePriceTierSerializer
)
from ..models import Brand, VehicleType, Feature, Vehicle, VehicleImage, InquiryData, FavoriteVehicle, VehiclePrice, \
    VehiclePriceTier
from ...reviews.models import VehicleReview


class BrandViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """
    ViewSet for Brand model
    Admin only for write operations
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ["primary"]

    @action(detail=True, methods=['get'])
    def vehicles(self, request, pk=None):
        """
        Get all vehicles for a specific brand
        """
        brand = self.get_object()
        vehicles = brand.vehicles.filter(is_active=True)
        serializer = VehicleListSerializer(vehicles, many=True)
        return Response(serializer.data)


class VehicleTypeViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """
    ViewSet for VehicleType model
    Admin only for write operations
    """
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


class FeatureViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """
    ViewSet for Feature model
    Admin only for write operations
    """
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class VehicleViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """
    ViewSet for Vehicle model
    Admin only for write operations
    """
    queryset = Vehicle.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'brand', 'year', 'body_type', 'engine_type',
        'transmission', 'is_featured',"staff_only","is_available","type"
    ]
    search_fields = ['model', 'color', 'brand__name']
    ordering_fields = ['price', 'year', 'created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get_queryset(self):
        if not self.request.user.is_staff:
            return Vehicle.objects.exclude(staff_only=True)
        return Vehicle.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return VehicleCreateUpdateSerializer
        return VehicleDetailSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get all featured vehicles
        """
        featured_vehicles = self.queryset.filter(is_featured=True)
        serializer = VehicleListSerializer(featured_vehicles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        """
        Filter vehicles by price range
        """
        min_price = request.query_params.get('min', None)
        max_price = request.query_params.get('max', None)

        vehicles = self.queryset
        if min_price:
            vehicles = vehicles.filter(price__gte=min_price)
        if max_price:
            vehicles = vehicles.filter(price__lte=max_price)

        serializer = VehicleListSerializer(vehicles, many=True)
        return Response(serializer.data)

class VehicleImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VehicleImage model
    """
    queryset = VehicleImage.objects.all()
    serializer_class = VehicleImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        # Handle form data for file uploads
        is_primary = request.data.get('is_primary') == 'true' or request.data.get('is_primary') == True

        # If setting this image as primary, unset any existing primary images
        if is_primary:
            vehicle_id = request.data.get('vehicle')
            if vehicle_id:
                VehicleImage.objects.filter(
                    vehicle_id=vehicle_id,
                    is_primary=True
                ).update(is_primary=False)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Handle form data for file uploads
        is_primary = request.data.get('is_primary') == 'true' or request.data.get('is_primary') == True

        # If setting this image as primary, unset any existing primary images
        if is_primary:
            instance = self.get_object()
            VehicleImage.objects.filter(
                vehicle_id=instance.vehicle_id,
                is_primary=True
            ).exclude(id=instance.id).update(is_primary=False)

        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_vehicle(self, request):
        """
        Get all images for a specific vehicle
        """
        vehicle_id = request.query_params.get('vehicle_id', None)
        if not vehicle_id:
            return Response(
                {"error": "vehicle_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        images = self.queryset.filter(vehicle_id=vehicle_id)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def set_as_primary(self, request, pk=None):
        """
        Set an image as the primary image for its vehicle
        """
        image = self.get_object()

        # Unset any existing primary images
        VehicleImage.objects.filter(
            vehicle_id=image.vehicle_id,
            is_primary=True
        ).update(is_primary=False)

        # Set this image as primary
        image.is_primary = True
        image.save()

        return Response(
            {"status": "success", "message": "Image set as primary"},
            status=status.HTTP_200_OK
        )




class InquiryDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InquiryData model
    """
    queryset = InquiryData.objects.all()
    serializer_class = InquiryDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['phone', 'whatsapp']


class FavoriteVehicleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FavoriteVehicle model
    """
    serializer_class = FavoriteVehicleSerializer
    permission_classes = [IsAuthenticated]
    model = FavoriteVehicle

    def get_queryset(self):
        """
        Get the favorite vehicles for the current user
        """
        user = self.request.user
        return FavoriteVehicle.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        """
        Get the favorite vehicle for the current user
        """
        user = self.request.user

        return FavoriteVehicle.objects.get_or_create(user=user)[0]

    @action(detail=False, methods=['post'])
    def add_to_favorites(self, request, *args, **kwargs):
        """
        Add a vehicle to the user's favorites
        """
        vehicle_id = request.data.get('vehicle_id')
        favorite = FavoriteVehicle.objects.get_or_create(user=self.request.user)[0]
        favorite.vehicles.add(vehicle_id)

        return Response(
            {"status": "success", "message": "Vehicle added to favorites"},
        )

    @action(detail=False, methods=['post'])
    def remove_from_favorites(self, request, *args, **kwargs):
        """
        Add a vehicle to the user's favorites
        """
        vehicle_id = request.data.get('vehicle_id')
        favorite = FavoriteVehicle.objects.get_or_create(user=self.request.user)[0]
        favorite.vehicles.remove(vehicle_id)

        return Response(
            {"status": "success", "message": "Vehicle removed from favorites"},
        )


class StatisticsAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        """
        Get statistics about vehicles
        """
        total_vehicles = Vehicle.objects.count()
        total_favorited_vehicles = FavoriteVehicle.vehicles.through.objects.count()
        total_reviews = VehicleReview.objects.count()

        stats = {
            "total_vehicles": total_vehicles,
            "total_favorited_vehicles": total_favorited_vehicles,
            "total_reviews": total_reviews,
        }

        return Response(stats)

class VehiclePriceViewSet(viewsets.ModelViewSet):
    queryset = VehiclePrice.objects.all()
    serializer_class = VehiclePriceSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = [
        "vehicle"
    ]


# views.py


class VehiclePriceTierViewSet(viewsets.ModelViewSet):
    queryset = VehiclePriceTier.objects.all()
    serializer_class = VehiclePriceTierSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle']  # 👈 Enables ?vehicle=<vehicle_id>
    permission_classes = [IsAuthenticatedOrReadOnly]
