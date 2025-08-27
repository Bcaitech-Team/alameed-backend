from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response

from .serializers import (
    CustomerDataSerializer,
    RentalCreateSerializer,
    RentalDetailSerializer,
    RentalUpdateSerializer, StaffRentalCreateSerializer
)
from ..models import CustomerData, Rental, Installment
from ...alerts.models import Notification


class CustomerDataViewSet(viewsets.ModelViewSet):
    queryset = CustomerData.objects.all()
    serializer_class = CustomerDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    # No filtering by user since customers are independent entities


class RentalViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__is_staff']


    def get_queryset(self):
        """
        All users can see rentals they created
        """
        return Rental.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            if self.request.user.is_staff:
                return StaffRentalCreateSerializer
            else:
                return RentalCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RentalUpdateSerializer
        return RentalDetailSerializer

    def perform_create(self, serializer):
        """
        Automatically set the created_by field to the current user
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Endpoint to confirm a rental
        """
        rental = self.get_object()
        if rental.status != 'pending':
            return Response(
                {"detail": "Only pending rentals can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rental.status = 'confirmed'
        rental.save()
        serializer = RentalDetailSerializer(rental)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Endpoint to start a rental (vehicle pickup)
        """
        rental = self.get_object()
        if rental.status != 'confirmed':
            return Response(
                {"detail": "Only confirmed rentals can be started"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rental.status = 'active'
        rental.save()
        serializer = RentalDetailSerializer(rental)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Endpoint to complete a rental (vehicle return)
        """
        rental = self.get_object()
        if rental.status != 'active':
            return Response(
                {"detail": "Only active rentals can be completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rental.status = 'completed'
        rental.save()
        serializer = RentalDetailSerializer(rental)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Endpoint to cancel a rental
        """
        rental = self.get_object()
        if rental.status in ['completed', 'cancelled']:
            return Response(
                {"detail": "This rental cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rental.status = 'cancelled'
        rental.save()
        serializer = RentalDetailSerializer(rental)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """
        Extend rental duration and generate new payment
        """
        rental = self.get_object()
        new_end_date = request.data.get("end_date")

        if not new_end_date:
            return Response(
                {"detail": "New end date is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.utils.dateparse import parse_datetime
        new_end_date = parse_datetime(new_end_date)

        if not new_end_date:
            return Response(
                {"detail": "Invalid end date format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure it's timezone-aware
        if timezone.is_naive(new_end_date):
            new_end_date = timezone.make_aware(new_end_date, timezone.get_current_timezone())

        # Compare correctly
        if new_end_date <= rental.end_date:
            return Response(
                {"detail": "End date must be later than the current end date" + str(rental.end_date)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # calculate new total
        delta = new_end_date - rental.start_date
        total_days = delta.days + (1 if delta.seconds > 0 else 0)

        price_tier = rental.vehicle.price_tiers.filter(
            min_days__lte=total_days
        ).filter(
            Q(max_days__gte=total_days) | Q(max_days__isnull=True)
        ).order_by('min_days').first()

        if price_tier:
            new_total = price_tier.price_per_day * total_days
        else:
            new_total = rental.vehicle.price * total_days

        additional_amount = new_total - (rental.total_price or 0)

        if additional_amount <= 0:
            return Response(
                {"detail": "No additional payment required"},
                status=status.HTTP_200_OK
            )

        with transaction.atomic():
            # Update rental
            rental.end_date = new_end_date
            rental.total_price = new_total
            rental.save()

            # Create new installment
            Installment.objects.create(
                rental=rental,
                due_date=new_end_date.date(),
                amount=additional_amount,
                user=rental.user,
            )

            # Notify user
            Notification.objects.create(
                user=rental.user,
                title="تم تمديد مدة الإيجار",
                message=(
                    f"تم تمديد مدة الإيجار حتى {new_end_date.date()}.\n"
                    f"يرجى دفع المبلغ الإضافي البالغ {additional_amount} دينار.\n"
                    "شكرًا لاختياركم خدمتنا."
                )
            )

        serializer = RentalDetailSerializer(rental)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RentalRequestsViewSet(viewsets.ModelViewSet):
    serializer_class = RentalDetailSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = [
        "user","user__is_staff"
    ]
    def get_queryset(self):
        """
        All users can see rentals they created
        """
        return Rental.objects.all()
