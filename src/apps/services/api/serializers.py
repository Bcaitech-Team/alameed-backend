from rest_framework import serializers

from ..models import (
    UpholsteryMaterial,
    UpholsteryType,
    UpholsteryGalleryImage,
    ServiceLocation,
    ServiceTimeSlot,
    UpholsteryBooking,
    BookingImage, UpholsteryCarModels, UpholsteryMaterialTypes,
)


class UpholsteryMaterialSerializer(serializers.ModelSerializer):
    """Serializer for upholstery materials"""

    class Meta:
        model = UpholsteryMaterial
        fields = [
            'id', 'name', 'description', 'image', 'price_per_seat',
            'available', 'durability_rating'
        ]


class UpholsteryTypeSerializer(serializers.ModelSerializer):
    """Serializer for upholstery service types"""

    class Meta:
        model = UpholsteryType
        fields = [
            'id', 'name', 'description', 'base_price',
            'estimated_hours', 'available'
        ]


class UpholsteryGalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images"""
    upholstery_type_name = serializers.CharField(source='upholstery_type.name', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)

    class Meta:
        model = UpholsteryGalleryImage
        fields = [
            'id', 'upholstery_type', 'upholstery_type_name',
            'material', 'material_name', 'image',
            'caption'

            , 'featured'
        ]


class ServiceLocationSerializer(serializers.ModelSerializer):
    """Serializer for service locations"""

    class Meta:
        model = ServiceLocation
        fields = [
            'id', 'name', 'address', 'phone', 'email',
            'working_hours_start', 'working_hours_end', 'is_active'
        ]


class ServiceTimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for service time slots"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServiceTimeSlot
        fields = [
            'id', 'location', 'location_name', 'date',
            'start_time', 'end_time', 'max_bookings',
            'current_bookings', 'is_available'
        ]


class BookingImageSerializer(serializers.ModelSerializer):
    """Serializer for booking before/after images"""

    class Meta:
        model = BookingImage
        fields = ['id', 'booking', 'image', 'is_before', 'caption']


# class UpholsteryBookingListSerializer(serializers.ModelSerializer):
#     """Serializer for booking list view (limited details)"""
#     upholstery_type_name = serializers.CharField(source='upholstery_type.name', read_only=True)
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#
#     class Meta:
#         model = UpholsteryBooking
#         fields = [
#             'id', 'seats', 'upholstery_type',
#             'upholstery_type_name', 'booking_date', 'status',
#             'status_display', 'total_price'
#         ]
#
#
# class UpholsteryBookingDetailSerializer(serializers.ModelSerializer):
#     """Detailed serializer for booking details"""
#     upholstery_type_name = serializers.CharField(source='upholstery_type.name', read_only=True)
#     primary_material_name = serializers.CharField(source='primary_material.name', read_only=True)
#     accent_material_name = serializers.SerializerMethodField()
#     time_slot_details = serializers.SerializerMethodField()
#     status_display = serializers.CharField(source='get_status_display', read_only=True)
#     images = BookingImageSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = UpholsteryBooking
#         fields = [
#             'id',
#             'upholstery_type', 'upholstery_type_name',
#             'primary_material', 'primary_material_name',
#             'accent_material', 'accent_material_name',
#             'time_slot', 'time_slot_details',
#             'user',
#             'booking_date', 'status', 'status_display',
#             'total_price', 'deposit_paid', 'notes',
#             'created_at', 'updated_at', 'completed_at',
#             'images'
#         ]
#         read_only_fields = [
#             'user'
#         ]
#
#     def get_accent_material_name(self, obj):
#         """Get accent material name if exists"""
#         if obj.accent_material:
#             return obj.accent_material.name
#         return None
#
#     def get_time_slot_details(self, obj):
#         """Get formatted time slot details"""
#         if obj.time_slot:
#             return {
#                 'location': obj.time_slot.location.name,
#                 'date': obj.time_slot.date,
#                 'start_time': obj.time_slot.start_time,
#                 'end_time': obj.time_slot.end_time
#             }
#         return None
#
#
#
# class UpholsteryBookingCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating bookings"""
#
#     class Meta:
#         model = UpholsteryBooking
#         fields = [
#             'upholstery_type', 'primary_material', 'accent_material',
#             'user', 'time_slot',
#             'notes', "seats"
#         ]
#
#     def validate(self, data):
#         """Validate booking data"""
#         # Check that time slot is available
#         time_slot = data.get('time_slot')
#         if time_slot and not time_slot.is_available:
#             raise serializers.ValidationError({
#                 'time_slot': 'This time slot is no longer available'
#             })
#
#         # Check that primary and accent materials are different
#         primary = data.get('primary_material')
#         accent = data.get('accent_material')
#         if primary and accent and primary == accent:
#             raise serializers.ValidationError({
#                 'accent_material': 'Primary and accent materials must be different'
#             })
#
#         return data
#
#     def create(self, validated_data):
#         """Create booking with calculated price"""
#         # Calculate price
#         seats = validated_data['seats']
#         upholstery_type = validated_data['upholstery_type']
#         primary_material = validated_data['primary_material']
#         accent_material = validated_data.get('accent_material')
#
#         # Base calculation same as in the model method
#         base_price = upholstery_type.base_price
#         material_cost = primary_material.price_per_seat * seats
#
#         total_price = base_price + material_cost
#
#         if accent_material:
#             accent_cost = accent_material.price_per_seat * seats * decimal.Decimal(0.3)
#             total_price += accent_cost
#
#         # Set calculated prices
#         validated_data['total_price'] = total_price
#         validated_data['deposit_paid'] = total_price * decimal.Decimal(0.2)  # 20% deposit
#
#         # Create and return the booking
#         return super().create(validated_data)
#
#     def save(self, **kwargs):
#         """Override save to set user"""
#         super().save(**kwargs)
#
#         # Set the user to the current authenticated user
#         if not self.instance.user:
#             print("11", self.context['request'].user)
#             self.instance.user = self.context['request'].user
#             self.instance.save()

class UpholsteryBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UpholsteryBooking
        fields = '__all__'
        read_only_fields = ["status"]

    def to_representation(self, instance):
        try:
            representation = super().to_representation(instance)
            representation['primary_material'] = instance.primary_material.name if instance.primary_material else None
            representation['material_type'] = instance.material_type.name if instance.material_type else None
            representation['car_model'] = instance.car_model.name if instance.car_model else None
            representation['user'] = instance.user.username if instance.user else None
        except:
            pass
        return representation


class UpholsteryCarModelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpholsteryCarModels
        fields = ['id', 'name']


class UpholsteryMaterialTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpholsteryMaterialTypes
        fields = ['id', 'name', 'image']
