from rest_framework import serializers
from ..models import Brand, VehicleType, Feature, Vehicle, VehicleImage, InquiryData


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
            'condition', 'is_featured', 'primary_image',"is_negotiable"
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None


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


class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating vehicles"""

    class Meta:
        model = Vehicle
        fields = '__all__'