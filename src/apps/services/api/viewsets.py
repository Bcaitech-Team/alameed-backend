from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from core.mixins import AdminOnlyMixin
from .serializers import (
    UpholsteryMaterialSerializer,
    UpholsteryTypeSerializer,
    UpholsteryGalleryImageSerializer,
    ServiceLocationSerializer,
    ServiceTimeSlotSerializer,
    # UpholsteryBookingListSerializer,
    # UpholsteryBookingDetailSerializer,
    # UpholsteryBookingCreateSerializer,
    BookingImageSerializer, UpholsteryBookingSerializer, UpholsteryCarModelsSerializer,
    UpholsteryMaterialTypesSerializer, CarImageSerializer, CarListingSerializer, VehicleComparisonSerializer
)
from ..models import (
    UpholsteryMaterial,
    UpholsteryType,
    UpholsteryGalleryImage,
    ServiceLocation,
    ServiceTimeSlot,
    UpholsteryBooking,
    BookingImage, UpholsteryCarModels, UpholsteryMaterialTypes, CarImage, CarListing, VehicleComparison
)


class UpholsteryMaterialViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for upholstery materials (admin only for create/update/delete)"""
    queryset = UpholsteryMaterial.objects.all()
    serializer_class = UpholsteryMaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['durability_rating', 'available']
    # search_fields = ['name', 'description']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UpholsteryTypeViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for upholstery service types (admin only for create/update/delete)"""
    queryset = UpholsteryType.objects.all()
    serializer_class = UpholsteryTypeSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['available']
    search_fields = ['name', 'description']
    permission_classes = [permissions.IsAuthenticated]



class UpholsteryGalleryImageViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for gallery images (admin only for create/update/delete)"""
    queryset = UpholsteryGalleryImage.objects.all()
    serializer_class = UpholsteryGalleryImageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['upholstery_type', 'material', 'featured']
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured gallery images"""
        featured = self.get_queryset().filter(featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class ServiceLocationViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for service locations (admin only for create/update/delete)"""
    queryset = ServiceLocation.objects.all()
    serializer_class = ServiceLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter to show only active locations for non-admin users"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


class ServiceTimeSlotViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for service time slots (admin only for create/update/delete)"""
    queryset = ServiceTimeSlot.objects.all()
    serializer_class = ServiceTimeSlotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location', 'date']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter to only show future time slots by default for non-admin users"""
        queryset = super().get_queryset()

        # Admin can see all time slots
        if self.request.user.is_staff:
            # Only filter by past/future if explicitly requested
            show_past = self.request.query_params.get('show_past', None)
            if show_past is not None:
                show_past = show_past.lower() == 'true'
                if not show_past:
                    queryset = queryset.filter(date__gte=timezone.now().date())
            return queryset

        # Non-admin users only see future time slots
        return queryset.filter(date__gte=timezone.now().date())

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available time slots"""
        queryset = self.get_queryset().filter(current_bookings__lt=models.F('max_bookings'))

        # Apply filters from query params
        location_id = request.query_params.get('location')
        date = request.query_params.get('date')

        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if date:
            queryset = queryset.filter(date=date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple time slots at once (admin only)"""

        # Validate data
        location_id = request.data.get('location')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        slot_times = request.data.get('slot_times', [])
        max_bookings = request.data.get('max_bookings', 1)

        if not all([location_id, start_date, end_date, slot_times]):
            return Response(
                {"detail": "Missing required fields: location, start_date, end_date, and slot_times"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create time slots for the specified date range and times
            from django.utils.dateparse import parse_date
            from datetime import timedelta

            location = ServiceLocation.objects.get(pk=location_id)
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            # Validate dates
            if not start_date or not end_date or start_date > end_date:
                return Response(
                    {"detail": "Invalid date range"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create slots
            created_slots = []
            current_date = start_date
            while current_date <= end_date:
                for slot in slot_times:
                    start_time = slot.get('start_time')
                    end_time = slot.get('end_time')

                    if not start_time or not end_time:
                        continue

                    time_slot, created = ServiceTimeSlot.objects.get_or_create(
                        location=location,
                        date=current_date,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'max_bookings': max_bookings,
                            'current_bookings': 0
                        }
                    )

                    if created:
                        created_slots.append(time_slot)

                # Move to next day
                current_date += timedelta(days=1)

            serializer = self.get_serializer(created_slots, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ServiceLocation.DoesNotExist:
            return Response(
                {"detail": "Location not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UpholsteryBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for upholstery bookings"""
    queryset = UpholsteryBooking.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', ]
    search_fields = ['user__first_name']
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpholsteryBookingSerializer

    # def get_serializer_class(self):
    #     """Use different serializers based on action"""
    #     if self.action == 'create':
    #         return UpholsteryBookingCreateSerializer
    #     elif self.action in ['retrieve', 'update', 'partial_update']:
    #         return UpholsteryBookingDetailSerializer
    #     return UpholsteryBookingListSerializer

    def get_queryset(self):
        """Filter bookings based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # Staff can see all bookings
        if user.is_staff:
            return queryset

        # Regular users can only see their own bookings
        return queryset.filter(customer_phone=user.phone)

    # def update(self, request, *args, **kwargs):
    #     """Restrict certain updates to admin only"""
    #     booking = self.get_object()
    #
    #     # Get the fields being updated
    #     updating_status = 'status' in request.data
    #
    #     # Only admin can update status
    #     if updating_status and not request.user.is_staff:
    #         return Response(
    #             {"detail": "Only staff can update booking status."},
    #             status=status.HTTP_403_FORBIDDEN
    #         )
    #
    #     # Regular users can only update their own bookings
    #     if not request.user.is_staff and booking.customer_phone != request.user.phone:
    #         return Response(
    #             {"detail": "You can only update your own bookings."},
    #             status=status.HTTP_403_FORBIDDEN
    #         )
    #
    #     # Prevent regular users from updating completed or in-progress bookings
    #     if not request.user.is_staff and booking.status in [
    #         UpholsteryBooking.STATUS_IN_PROGRESS,
    #         UpholsteryBooking.STATUS_COMPLETED
    #     ]:
    #         return Response(
    #             {"detail": "Cannot update bookings that are in progress or completed."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     return super().update(request, *args, **kwargs)

    # @action(detail=True, methods=['post'])
    # def cancel(self, request, pk=None):
    #     """Cancel a booking"""
    #     booking = self.get_object()
    #
    #     # Only allow cancellation of pending or confirmed bookings
    #     if booking.status not in [UpholsteryBooking.STATUS_PENDING, UpholsteryBooking.STATUS_CONFIRMED]:
    #         return Response(
    #             {"detail": "Cannot cancel a booking that is already in progress or completed."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     booking.status = UpholsteryBooking.STATUS_CANCELLED
    #     booking.save()
    #
    #     return Response({"status": "booking cancelled"})
    #
    # @action(detail=True, methods=['post'])
    # def update_status(self, request, pk=None):
    #     """Update booking status (staff only)"""
    #     if not request.user.is_staff:
    #         return Response(
    #             {"detail": "You do not have permission to perform this action."},
    #             status=status.HTTP_403_FORBIDDEN
    #         )
    #
    #     booking = self.get_object()
    #     new_status = request.data.get('status')
    #
    #     if not new_status or new_status not in dict(UpholsteryBooking.STATUS_CHOICES):
    #         return Response(
    #             {"detail": "Invalid status value."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #
    #     booking.status = new_status
    #
    #     # If status is completed, set completion time
    #     if new_status == UpholsteryBooking.STATUS_COMPLETED and not booking.completed_at:
    #         booking.completed_at = timezone.now()
    #
    #     booking.save()
    #     serializer = UpholsteryBookingDetailSerializer(booking)
    #     return Response(serializer.data)
    #
    # @action(detail=False, methods=['get'])
    # def price_estimate(self, request):
    #     """Calculate price estimate based on query parameters"""
    #     # Get parameters
    #     upholstery_type_id = request.query_params.get('upholstery_type')
    #     primary_material_id = request.query_params.get('primary_material')
    #     accent_material_id = request.query_params.get('accent_material')
    #     seats = request.query_params.get('seats')
    #
    #     # Validate parameters
    #     errors = {}
    #     if not upholstery_type_id:
    #         errors['upholstery_type'] = ['This parameter is required']
    #     if not primary_material_id:
    #         errors['primary_material'] = ['This parameter is required']
    #     if not seats:
    #         errors['seats'] = ['This parameter is required']
    #
    #     if errors:
    #         return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    #
    #     try:
    #         seats = int(seats)
    #         if seats <= 0:
    #             return Response({'seats': ['Number of seats must be at least 1']}, status=status.HTTP_400_BAD_REQUEST)
    #     except ValueError:
    #         return Response({'seats': ['Must be a valid integer']}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # Get objects
    #     try:
    #         upholstery_type = UpholsteryType.objects.get(id=upholstery_type_id)
    #         primary_material = UpholsteryMaterial.objects.get(id=primary_material_id)
    #         accent_material = None
    #         if accent_material_id:
    #             accent_material = UpholsteryMaterial.objects.get(id=accent_material_id)
    #     except (UpholsteryType.DoesNotExist, UpholsteryMaterial.DoesNotExist):
    #         return Response({'detail': 'One or more objects not found'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     # Calculate price
    #     base_price = upholstery_type.base_price
    #     material_cost = primary_material.price_per_seat * seats
    #
    #     total_price = base_price + material_cost
    #
    #     if accent_material:
    #         if accent_material == primary_material:
    #             return Response(
    #                 {'accent_material': ['Primary and accent materials must be different']},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         accent_cost = accent_material.price_per_seat * seats * 0.3  # 30% for accent
    #         total_price += accent_cost
    #
    #     # Return price estimate
    #     return Response({
    #         'upholstery_type': upholstery_type.name,
    #         'primary_material': primary_material.name,
    #         'accent_material': accent_material.name if accent_material else None,
    #         'seats': seats,
    #         'base_price': float(base_price),
    #         'material_cost': float(material_cost),
    #         'accent_cost': float(accent_material.price_per_seat * seats * 0.3) if accent_material else 0,
    #         'total_price': float(total_price),
    #         'estimated_deposit': float(total_price * 0.2),  # 20% deposit
    #         'estimated_hours': upholstery_type.estimated_hours
    #     })


class BookingImageViewSet(AdminOnlyMixin, viewsets.ModelViewSet):
    """ViewSet for booking images (before/after) - admin only for create/update/delete"""
    queryset = BookingImage.objects.all()
    serializer_class = BookingImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['booking', 'is_before']

    def get_queryset(self):
        """Filter images based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # Staff can see all images
        if user.is_staff:
            return queryset

        # Regular users can only see images for their own bookings
        return queryset.filter(booking__customer_phone=user.phone)


class UpholsteryCarModelsViewSet(viewsets.ModelViewSet):
    queryset = UpholsteryCarModels.objects.all()
    serializer_class = UpholsteryCarModelsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['upholstery_material']


class UpholsteryMaterialTypesViewSet(viewsets.ModelViewSet):
    queryset = UpholsteryMaterialTypes.objects.all()
    serializer_class = UpholsteryMaterialTypesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['upholstery_material', 'upholstery_car_model']


class CarListingViewSet(viewsets.ModelViewSet):
    queryset = CarListing.objects.all()
    serializer_class = CarListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fuel_type', 'transmission', 'year', 'status', 'body_condition', 'previous_owners_count',"user"]
    search_fields = ['brand_model', 'color', 'seller_name', 'accessories']
    ordering_fields = ['created_at', 'price', 'year', 'mileage']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = CarListing.objects.all()
        return queryset

    def perform_create(self, serializer):
        """Set the user when creating a car listing"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Ensure user can only update their own listings"""
        instance = self.get_object()
        if (self.request.user == instance.user or
                self.request.user.is_staff or
                instance.user is None):
            serializer.save()
        else:
            raise PermissionError("You can only update your own listings")

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """Get current user's car listings"""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'},
                            status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_sold(self, request, pk=None):
        """Mark a car listing as sold"""
        car_listing = self.get_object()

        if (request.user != car_listing.user and
                not request.user.is_staff and
                car_listing.user is not None):
            return Response({'detail': 'Permission denied'},
                            status=status.HTTP_403_FORBIDDEN)

        car_listing.status = 'sold'
        car_listing.save()

        return Response({'status': 'Car marked as sold'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a car listing"""
        car_listing = self.get_object()

        if (request.user != car_listing.user and
                not request.user.is_staff and
                car_listing.user is not None):
            return Response({'detail': 'Permission denied'},
                            status=status.HTTP_403_FORBIDDEN)

        car_listing.status = 'active'
        car_listing.save()

        return Response({'status': 'Car listing activated'})


class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Ensure user can only add images to their own listings"""
        car_listing = serializer.validated_data['car_listing']
        if (self.request.user == car_listing.user or
                self.request.user.is_staff or
                car_listing.user is None):
            serializer.save()
        else:
            raise PermissionError("You can only add images to your own listings")

    def perform_update(self, serializer):
        """Ensure user can only update images of their own listings"""
        instance = self.get_object()
        if (self.request.user == instance.car_listing.user or
                self.request.user.is_staff or
                instance.car_listing.user is None):
            serializer.save()
        else:
            raise PermissionError("You can only update images of your own listings")

    def perform_destroy(self, instance):
        """Ensure user can only delete images of their own listings"""
        if (self.request.user == instance.car_listing.user or
                self.request.user.is_staff or
                instance.car_listing.user is None):
            instance.delete()
        else:
            raise PermissionError("You can only delete images of your own listings")


class VehicleComparisonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for comparing multiple vehicles.
    Each user has a single comparison object.
    """
    serializer_class = VehicleComparisonSerializer
    model = VehicleComparison

    def get_queryset(self):
        """
        Get the comparison object for the current user
        """
        return VehicleComparison.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Override list to behave like retrieve
        """
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        """
        Get or create the user's comparison object
        """
        return VehicleComparison.objects.get_or_create(user=self.request.user)[0]

    @action(detail=False, methods=['post'])
    def add_vehicle(self, request):
        """
        Add a vehicle to the comparison list
        """
        vehicle_id = request.data.get('vehicle_id')
        comparison = self.get_object()
        comparison.vehicles.add(vehicle_id)

        return Response({"status": "success", "message": "Vehicle added to comparison"})

    @action(detail=False, methods=['post'])
    def remove_vehicle(self, request):
        """
        Remove a vehicle from the comparison list
        """
        vehicle_id = request.data.get('vehicle_id')
        comparison = self.get_object()
        comparison.vehicles.remove(vehicle_id)

        return Response({"status": "success", "message": "Vehicle removed from comparison"})

    @action(detail=False, methods=['post'])
    def reset(self, request):
        """
        Clear all vehicles from the comparison list
        """
        comparison = self.get_object()
        comparison.vehicles.clear()

        return Response({"status": "success", "message": "Comparison list reset"})
