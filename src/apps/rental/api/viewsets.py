from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    CustomerDataSerializer,
    RentalCreateSerializer,
    RentalDetailSerializer,
    RentalUpdateSerializer
)
from ..models import CustomerData, Rental


class CustomerDataViewSet(viewsets.ModelViewSet):
    queryset = CustomerData.objects.all()
    serializer_class = CustomerDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    # No filtering by user since customers are independent entities


class RentalViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        """
        All users can see rentals they created
        """
        return Rental.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
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


class RentalRequestsViewSet(viewsets.ModelViewSet):
    serializer_class = RentalDetailSerializer

    def get_queryset(self):
        """
        All users can see rentals they created
        """
        return Rental.objects.all()

