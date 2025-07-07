from rest_framework import serializers

from ..models import CustomerData, Rental, Installment
from ...users.api.serializers import SimpleUserSerializer
from ...vehicles.api.serializers import VehicleDetailSerializer


class CustomerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerData
        fields = [
            'id', 'first_name', 'middle_name', 'last_name', 'phone_number', 'id_number',
            'nationality', 'license_front_photo', 'license_back_photo',
            'id_front_photo', 'id_back_photo', 'created_at', 'updated_at'
        ]

class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ['id', 'due_date', 'amount', 'is_paid']

class RentalCreateSerializer(serializers.ModelSerializer):
    customer_data = CustomerDataSerializer()

    class Meta:
        model = Rental
        fields = [
            'customer_data', 'vehicle', 'start_date', 'end_date',"inspection_form",
        ]

    def create(self, validated_data):
        """
        Override the create method to handle nested customer_data
        """
        # Extract customer data from validated_data
        customer_data = validated_data.pop('customer_data')

        # Create a new customer with the provided data
        customer = CustomerData.objects.create(**customer_data)

        # Create the rental with the customer and remaining data
        rental = Rental.objects.create(customer_data=customer, **validated_data)

        return rental

    def validate(self, data):
        """
        Check if the vehicle is available for the requested dates
        """
        vehicle = data['vehicle']
        start_date = data['start_date']
        end_date = data['end_date']

        # Check if end date is after start date
        if end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date must be after start date"})

        # Check if vehicle is available for the requested dates
        conflicting_rentals = Rental.objects.filter(
            vehicle=vehicle,
            status__in=['pending', 'confirmed', 'active'],
        ).exclude(
            end_date__lt=start_date
        ).exclude(
            start_date__gt=end_date
        )

        if conflicting_rentals.exists():
            raise serializers.ValidationError(
                {"vehicle": "This vehicle is not available for the selected dates"}
            )

        return data

class StaffRentalCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rental
        fields = [
             'vehicle', 'start_date', 'end_date',
        ]

    def validate(self, data):
        """
        Check if the vehicle is available for the requested dates
        """
        vehicle = data['vehicle']
        start_date = data['start_date']
        end_date = data['end_date']

        # Check if end date is after start date
        if end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date must be after start date"})

        if vehicle.is_available is False:
            raise serializers.ValidationError(
                {"vehicle": "This vehicle is not available for the selected dates"}
            )

        return data

class RentalDetailSerializer(serializers.ModelSerializer):
    customer_data = CustomerDataSerializer(read_only=True)
    vehicle = VehicleDetailSerializer(read_only=True)
    user = SimpleUserSerializer(read_only=True)
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = Rental
        fields = [
            'id', 'customer_data', 'vehicle', 'user',
            'start_date', 'end_date', 'status', 'total_price',
            'created_at', 'updated_at', 'inspection_form',
            'installments',
        ]



class RentalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['status',"inspection_form",]
