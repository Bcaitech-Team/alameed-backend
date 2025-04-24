from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    """Brand model to categorize vehicles by manufacturer"""
    name = models.CharField(_("Brand Name"), max_length=100)
    logo = models.ImageField(_("Brand Logo"), upload_to='brands/', blank=True, null=True)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    """Vehicle type model (SUV, Sedan, etc.)"""
    name = models.CharField(_("Type Name"), max_length=50)

    def __str__(self):
        return self.name




class Feature(models.Model):
    """Features that can be assigned to vehicles"""
    name = models.CharField(_("Feature Name"), max_length=100)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """Main vehicle model with all specifications"""
    # Basic Info
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="vehicles")
    model = models.CharField(_("Model Name"), max_length=100)
    year = models.PositiveIntegerField(_("Year"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=3)
    currency = models.CharField(_("Currency"), max_length=10, default="BHD")

    # Vehicle Details
    body_type = models.CharField(_("Body type"), max_length=100)
    color = models.CharField(_("Color"), max_length=50)
    mileage = models.PositiveIntegerField(_("Mileage (KM)"))

    # Technical Specifications
    engine_type = models.CharField(_("Engine Type"), max_length=50, choices=[
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ])
    engine_capacity = models.DecimalField(_("Engine Capacity (L)"), max_digits=3, decimal_places=1)
    cylinders = models.PositiveSmallIntegerField(_("Cylinders"))
    transmission = models.CharField(_("Transmission"), max_length=20, choices=[
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('cvt', 'CVT'),
        ('dual_clutch', 'Dual Clutch')
    ])
    seats = models.PositiveSmallIntegerField(_("Number of Seats"))

    # Status and Condition
    condition = models.CharField(_("Condition"), max_length=20, choices=[
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-owned')
    ])
    condition_ar = models.CharField(_("Arabic Condition"), max_length=20)

    # Insurance and Registration
    insurance_expiry = models.DateField(_("Insurance Expiry"), blank=True, null=True)

    # Features
    features = models.ManyToManyField(Feature, related_name="vehicles", blank=True)

    # Inquiry Data
    inquiry_data = models.ForeignKey('InquiryData', on_delete=models.CASCADE, related_name="vehicles", blank=True, null=True)

    # Meta Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(_("Featured"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    is_negotiable = models.BooleanField(_("Negotiable"), default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} {self.year}"


class VehicleImage(models.Model):
    """Additional images for the vehicle"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("Image"), upload_to='vehicles/gallery/')
    is_primary = models.BooleanField(_("Primary Image"), default=False)
    caption = models.CharField(_("Caption"), max_length=255, blank=True)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Image for {self.vehicle}"


class InquiryData(models.Model):
    """Customer inquiries about vehicles"""

    phone = models.CharField(_("Phone Number"), max_length=20)
    whatsapp = models.CharField(_("WhatsApp Number"), max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if not self.whatsapp:
            self.whatsapp = self.phone
        super().save(*args, **kwargs)
