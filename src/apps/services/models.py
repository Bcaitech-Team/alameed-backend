import decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UpholsteryMaterial(models.Model):
    """Materials available for car upholstery"""
    name = models.CharField(_("Material Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Material Image"), upload_to='upholstery/materials/', blank=True, null=True)
    price_per_seat = models.DecimalField(_("Price per Seat"), max_digits=8, decimal_places=3)
    available = models.BooleanField(_("Available"), default=True)

    # Additional properties
    durability_rating = models.PositiveSmallIntegerField(
        _("Durability Rating"),
        validators=[MinValueValidator(1)],
        choices=[(i, str(i)) for i in range(1, 6)],  # 1-5 rating
        help_text=_("Rating from 1 (least durable) to 5 (most durable)")
    )

    class Meta:
        verbose_name = _("Upholstery Material")
        verbose_name_plural = _("Upholstery Materials")
        ordering = ['name']

    def __str__(self):
        return self.name


class UpholsteryType(models.Model):
    """Types of upholstery services offered (e.g., Full Interior, Seats Only, etc.)"""
    name = models.CharField(_("Type Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    base_price = models.DecimalField(_("Base Price"), max_digits=8, decimal_places=3)
    estimated_hours = models.PositiveSmallIntegerField(_("Estimated Hours"), default=4)
    available = models.BooleanField(_("Available"), default=True)

    # Example service types: Full Interior, Seats Only, Dashboard, Door Panels, etc.

    class Meta:
        verbose_name = _("Upholstery Type")
        verbose_name_plural = _("Upholstery Types")
        ordering = ['name']

    def __str__(self):
        return self.name


class UpholsteryGalleryImage(models.Model):
    """Example images of completed upholstery work"""
    upholstery_type = models.ForeignKey(
        UpholsteryType,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )
    material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )
    image = models.ImageField(_("Image"), upload_to='upholstery/gallery/')
    caption = models.CharField(_("Caption"), max_length=255, blank=True)
    vehicle_info = models.CharField(_("Vehicle Information"), max_length=255, blank=True)
    featured = models.BooleanField(_("Featured"), default=False)

    class Meta:
        verbose_name = _("Upholstery Gallery Image")
        verbose_name_plural = _("Upholstery Gallery Images")
        ordering = ['-featured', 'id']

    def __str__(self):
        return f"{self.upholstery_type} with {self.material}"


class ServiceLocation(models.Model):
    """Locations where upholstery service can be performed"""
    name = models.CharField(_("Location Name"), max_length=100)
    address = models.TextField(_("Address"))
    phone = models.CharField(_("Phone"), max_length=20)
    email = models.EmailField(_("Email"), blank=True)
    working_hours_start = models.TimeField(_("Working Hours Start"))
    working_hours_end = models.TimeField(_("Working Hours End"))
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Service Location")
        verbose_name_plural = _("Service Locations")
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceTimeSlot(models.Model):
    """Available time slots for upholstery service appointments"""
    location = models.ForeignKey(
        ServiceLocation,
        on_delete=models.CASCADE,
        related_name="time_slots"
    )
    date = models.DateField(_("Date"))
    start_time = models.TimeField(_("Start Time"))
    end_time = models.TimeField(_("End Time"))
    max_bookings = models.PositiveSmallIntegerField(_("Maximum Bookings"), default=1)
    current_bookings = models.PositiveSmallIntegerField(_("Current Bookings"), default=0)

    class Meta:
        verbose_name = _("Service Time Slot")
        verbose_name_plural = _("Service Time Slots")
        ordering = ['date', 'start_time']
        unique_together = ['location', 'date', 'start_time']

    def __str__(self):
        return f"{self.location} - {self.date} {self.start_time}"

    @property
    def is_available(self):
        return self.current_bookings < self.max_bookings


class UpholsteryBooking(models.Model):
    """Bookings for upholstery services"""
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]

    # Relations
    # vehicle = models.ForeignKey(
    #     'Vehicle',  # Your existing Vehicle model
    #     on_delete=models.CASCADE,
    #     related_name="upholstery_bookings"
    # )
    seats = models.PositiveSmallIntegerField(_("Number of Seats"), default=1)
    upholstery_type = models.ForeignKey(
        UpholsteryType,
        on_delete=models.PROTECT,
        related_name="bookings"
    )
    primary_material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.PROTECT,
        related_name="primary_bookings"
    )
    accent_material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.PROTECT,
        related_name="accent_bookings",
        blank=True,
        null=True
    )
    time_slot = models.ForeignKey(
        ServiceTimeSlot,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    # Customer info
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="upholstery_bookings",
        blank=True,
        null=True
    )

    # Booking details
    booking_date = models.DateTimeField(_("Booking Date"), auto_now_add=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=3)
    deposit_paid = models.DecimalField(_("Deposit Paid"), max_digits=10, decimal_places=3, default=0)
    notes = models.TextField(_("Special Requirements"), blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(_("Completion Time"), blank=True, null=True)

    class Meta:
        verbose_name = _("Upholstery Booking")
        verbose_name_plural = _("Upholstery Bookings")
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking #{self.id}"

    def save(self, *args, **kwargs):
        # Update the time slot's current bookings
        is_new = self.pk is None
        if is_new and self.time_slot:
            self.time_slot.current_bookings += 1
            self.time_slot.save()

        super().save(*args, **kwargs)

    def calculate_total_price(self):
        """Calculate the total price based on the upholstery type, materials, and vehicle seats"""
        base_price = self.upholstery_type.base_price
        seats = self.seats  # Using the seats field from your Vehicle model

        # Add the cost of the primary material for each seat
        material_cost = self.primary_material.price_per_seat * seats

        # If there's an accent material, add a portion of its cost
        if self.accent_material:
            accent_cost = self.accent_material.price_per_seat * seats * decimal.Decimal(
                0.3)  # Assuming accent is 30% of the upholstery
            total = base_price + material_cost + accent_cost
        else:
            total = base_price + material_cost

        return total


class BookingImage(models.Model):
    """Before and after images for upholstery bookings"""
    booking = models.ForeignKey(
        UpholsteryBooking,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(_("Image"), upload_to='upholstery/bookings/')
    is_before = models.BooleanField(_("Before Image"), default=True)
    caption = models.CharField(_("Caption"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Booking Image")
        verbose_name_plural = _("Booking Images")
        ordering = ['is_before', 'id']

    def __str__(self):
        status = "Before" if self.is_before else "After"
        return f"{status} image for Booking #{self.booking.id}"
