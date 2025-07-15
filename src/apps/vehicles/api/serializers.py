from django.utils import timezone
from rest_framework import serializers

from ..models import Brand, VehicleType, Feature, Vehicle, VehicleImage, InquiryData, FavoriteVehicle, VehiclePrice, \
    VehiclePriceTier


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'


class InquiryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryData
        fields = '__all__'


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = '__all__'


class VehicleImageListSerializer(serializers.ModelSerializer):
    """Serializer for listing vehicle images (used in VehicleDetailSerializer)"""

    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'is_primary', 'caption']


class VehicleListSerializer(serializers.ModelSerializer):
    """Serializer for listing vehicles with minimal information"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'brand', 'brand_name', 'model', 'year', 'price', 'currency',
            'body_type', 'color', 'mileage', 'engine_type', 'transmission',
            'condition', 'is_featured', 'primary_image', "is_negotiable", "created_at", "contract_type", "staff_only",
            "is_available", "status", "available_units",
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data["current_price"] = instance.current_price
        return data

class VehicleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for vehicle with all related information"""
    brand_details = BrandSerializer(source='brand', read_only=True)
    features_list = FeatureSerializer(source='features', many=True, read_only=True)
    images = VehicleImageListSerializer(many=True, read_only=True)
    inquiry_data_details = InquiryDataSerializer(source='inquiry_data', read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'
        extra_fields = [
            'brand_details', 'features_list', 'images', 'inquiry_data_details'
        ]

    def to_representation(self, instance):
        data= super().to_representation(instance)
        data["current_price"] = instance.current_price
        return data

class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating vehicles with images"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,  # required=False lets PATCH skip this field
    )
    captions = serializers.ListField(
        child=serializers.CharField(required=False, allow_blank=True),
        write_only=True,
        required=False,
    )
    primary_image_index = serializers.IntegerField(
        write_only=True,
        required=False,
        default=0,
        min_value=0,
    )

    class Meta:
        model = Vehicle
        fields = '__all__'

    def validate(self, data):
        """Validate only if images are provided or on create"""
        images = data.get('images', None)
        primary_index = data.get('primary_image_index', 0)

        if self.instance is None:
            # CREATE (POST)
            if not images:
                raise serializers.ValidationError({"images": "At least one image is required."})
        else:
            # UPDATE (PATCH/PUT)
            if images is not None and not images:
                raise serializers.ValidationError({"images": "At least one image is required."})

        if images is not None:
            if primary_index >= len(images):
                raise serializers.ValidationError(
                    {"primary_image_index": f"Primary image index must be less than {len(images)}"}
                )

            captions = data.get('captions', [])
            if captions and len(captions) != len(images):
                raise serializers.ValidationError(
                    {"captions": f"Number of captions ({len(captions)}) must match number of images ({len(images)})"}
                )

        return data

    def create(self, validated_data):
        """Create vehicle and associated images"""
        images = validated_data.pop('images', [])
        captions = validated_data.pop('captions', [])
        primary_index = validated_data.pop('primary_image_index', 0)

        features = validated_data.pop('features', None)

        vehicle = Vehicle.objects.create(**validated_data)

        if features is not None:
            vehicle.features.set(features)

        for i, image_data in enumerate(images):
            caption = captions[i] if i < len(captions) else ""
            VehicleImage.objects.create(
                vehicle=vehicle,
                image=image_data,
                caption=caption,
                is_primary=(i == primary_index)
            )

        return vehicle

    def update(self, instance, validated_data):
        """Update vehicle and handle image updates if provided"""
        images = validated_data.pop('images', None)
        captions = validated_data.pop('captions', [])
        primary_index = validated_data.pop('primary_image_index', 0)

        features = validated_data.pop('features', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if features is not None:
            instance.features.set(features)

        if images is not None:
            # If you want to replace old images, you can uncomment this:
            # instance.images.all().delete()
            for i, image_data in enumerate(images):
                caption = captions[i] if i < len(captions) else ""
                VehicleImage.objects.create(
                    vehicle=instance,
                    image=image_data,
                    caption=caption,
                    is_primary=(i == primary_index)
                )

        return instance


class FavoriteVehicleSerializer(serializers.ModelSerializer):
    """Serializer for user's favorite vehicles"""

    class Meta:
        model = FavoriteVehicle
        fields = "__all__"

    def save(self, **kwargs):
        """Override save to set user"""
        kwargs['user'] = self.context['request'].user
        super().save(**kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['vehicles'] = VehicleListSerializer(instance.vehicles, many=True).data
        return representation


class VehiclePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePrice
        fields = ['id', 'vehicle', 'price', 'start_date']

    def validate_start_date(self, value):
        today = timezone.now().date()
        if value < today:
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def validate(self, data):
        vehicle = data.get('vehicle')
        start_date = data.get('start_date')

        # When updating, exclude current instance
        qs = VehiclePrice.objects.filter(vehicle=vehicle, start_date=start_date)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Price for this vehicle already exists on this date.")
        return data


class VehiclePriceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclePriceTier
        fields = ['id', 'vehicle', 'min_days', 'max_days', 'price_per_day']
