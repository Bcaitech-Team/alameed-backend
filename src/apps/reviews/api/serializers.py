from rest_framework import serializers
from ..models import VehicleReview

class VehicleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleReview
        fields = '__all__'
