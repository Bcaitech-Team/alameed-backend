"""
URL configuration for chat_bot_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

from src.apps.rental.api.viewsets import RentalViewSet, RentalRequestsViewSet
from src.apps.reviews.api.viewsets import VehicleReviewViewSet
from src.apps.services.api.viewsets import UpholsteryMaterialViewSet, UpholsteryTypeViewSet, \
    UpholsteryGalleryImageViewSet, ServiceLocationViewSet, ServiceTimeSlotViewSet, UpholsteryBookingViewSet, \
    BookingImageViewSet, UpholsteryMaterialTypesViewSet, UpholsteryCarModelsViewSet, CarListingViewSet, \
    VehicleComparisonViewSet
from src.apps.support.api.viewsets import TicketViewSet, ChatMessageViewSet, ContactMessageViewSet
from src.apps.users.api.viewsets import UsersViewSet
from src.apps.vehicles.api.viewsets import BrandViewSet, FeatureViewSet, VehicleTypeViewSet, VehicleImageViewSet, \
    VehicleViewSet, InquiryDataViewSet, FavoriteVehicleViewSet, StatisticsAPIView, VehiclePriceViewSet, \
    VehiclePriceTierViewSet

router = DefaultRouter()
router.register('vehicles/brands', BrandViewSet)
router.register('vehicles/vehicle-types', VehicleTypeViewSet)
router.register('vehicles/features', FeatureViewSet)
router.register('vehicles/vehicles', VehicleViewSet)
router.register('vehicles/vehicle-prices', VehiclePriceViewSet)
router.register('vehicles/vehicle-images', VehicleImageViewSet)
router.register('vehicles/inquiries', InquiryDataViewSet)
router.register('vehicles/favorite', FavoriteVehicleViewSet, basename='favorite-vehicle')
router.register(r'vehicles/price-tiers', VehiclePriceTierViewSet, basename='price-tier')
router.register('reviews/vehicle-review', VehicleReviewViewSet)
router.register('services/upholstery/materials', UpholsteryMaterialViewSet, basename='api-material')
router.register('services/upholstery/types', UpholsteryTypeViewSet, basename='api-type')
router.register('services/upholstery/gallery', UpholsteryGalleryImageViewSet, basename='api-gallery')
router.register('services/upholstery/locations', ServiceLocationViewSet, basename='api-location')
router.register('services/upholstery/time-slots', ServiceTimeSlotViewSet, basename='api-timeslot')
router.register('services/upholstery/bookings', UpholsteryBookingViewSet, basename='api-booking')
router.register('services/upholstery/booking-images', BookingImageViewSet, basename='api-booking-image')
router.register(r'support/tickets', TicketViewSet, basename='ticket')
router.register(r'support/messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'support/contact', ContactMessageViewSet, basename='contact')
router.register(r'rentals/rentals', RentalViewSet, basename='rental')
router.register(r'rentals/rentals-requests', RentalRequestsViewSet, basename='rental-requests')
router.register(r'services/upholstery/car-models', UpholsteryCarModelsViewSet, basename='api-car-models')
router.register(r'services/upholstery/material-types', UpholsteryMaterialTypesViewSet, basename='api-material-types')
router.register(r'services/car-listings', CarListingViewSet, basename='car-listing')
router.register(r'services/car-comparison', VehicleComparisonViewSet, basename='vehicle-comparison')
router.register('alerts/devices', FCMDeviceAuthorizedViewSet)
router.register('users/users', UsersViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/authentication/', include('dj_rest_auth.urls')),
    path('api/authentication/registration/', include('dj_rest_auth.registration.urls')),
    path('api/vehicles/statistics/', StatisticsAPIView.as_view(), name='statistics'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)