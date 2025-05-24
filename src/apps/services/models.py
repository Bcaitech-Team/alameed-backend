from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UpholsteryMaterial(models.Model):
    """Materials available for car upholstery"""
    name = models.CharField(_("Material Name"), max_length=100)
    # description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Material Image"), upload_to='upholstery/materials/', blank=True, null=True)
    price = models.DecimalField(_("Price"), max_digits=8, decimal_places=3, default=240)

    # price_per_seat = models.DecimalField(_("Price per Seat"), max_digits=8, decimal_places=3)
    # available = models.BooleanField(_("Available"), default=True)

    # Additional properties
    # durability_rating = models.PositiveSmallIntegerField(
    #     _("Durability Rating"),
    #     validators=[MinValueValidator(1)],
    #     choices=[(i, str(i)) for i in range(1, 6)],  # 1-5 rating
    #     help_text=_("Rating from 1 (least durable) to 5 (most durable)")
    # )

    class Meta:
        verbose_name = _("Upholstery Material")
        verbose_name_plural = _("Upholstery Materials")
        # ordering = ['name']

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


class UpholsteryCarModels(models.Model):
    name = models.CharField(_("Car Model Name"), max_length=100)
    upholstery_material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.CASCADE,
        related_name="car_models"
    )


    class Meta:
        verbose_name = _("Upholstery Car Model")
        verbose_name_plural = _("Upholstery Car Models")
        ordering = ['name']

    def __str__(self):
        return self.name


class UpholsteryMaterialTypes(models.Model):
    name = models.CharField(_("Material Type Name"), max_length=100)
    image = models.ImageField(_("Material Type Image"), upload_to='upholstery/material_types/', blank=True, null=True)
    upholstery_material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.CASCADE,
        related_name="material_types"
    )
    upholstery_car_model = models.ForeignKey(UpholsteryCarModels, on_delete=models.CASCADE,
                                             related_name="material_types")
    class Meta:
        verbose_name = _("Upholstery Material Type")
        verbose_name_plural = _("Upholstery Material Types")
        ordering = ['name']

    def __str__(self):
        return self.name


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
    # seats = models.PositiveSmallIntegerField(_("Number of Seats"), default=1)
    # upholstery_type = models.ForeignKey(
    #     UpholsteryType,
    #     on_delete=models.PROTECT,
    #     related_name="bookings"
    # )
    primary_material = models.ForeignKey(
        UpholsteryMaterial,
        on_delete=models.PROTECT,
        related_name="primary_bookings",

    )
    material_type = models.ForeignKey(
        UpholsteryMaterialTypes,
        on_delete=models.PROTECT,
        related_name="material_bookings",

    )
    car_model = models.ForeignKey(
        UpholsteryCarModels,
        on_delete=models.PROTECT,
        related_name="model_bookings",

    )
    # accent_material = models.ForeignKey(
    #     UpholsteryMaterial,
    #     on_delete=models.PROTECT,
    #     related_name="accent_bookings",
    #     blank=True,
    #     null=True
    # )
    # time_slot = models.ForeignKey(
    #     ServiceTimeSlot,
    #     on_delete=models.PROTECT,
    #     related_name="bookings"
    # )

    # Customer info
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="upholstery_bookings",
        blank=True,
        null=True
    )

    # Booking details
    # booking_date = models.DateTimeField(_("Booking Date"), auto_now_add=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    # total_price = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=3)
    # deposit_paid = models.DecimalField(_("Deposit Paid"), max_digits=10, decimal_places=3, default=0)
    # notes = models.TextField(_("Special Requirements"), blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(_("Completion Time"), blank=True, null=True)

    class Meta:
        verbose_name = _("Upholstery Booking")
        verbose_name_plural = _("Upholstery Bookings")
        # ordering = ['-booking_date']

    def __str__(self):
        return f"Booking #{self.id}"

    # def save(self, *args, **kwargs):
    #     # Update the time slot's current bookings
    #     is_new = self.pk is None
    #     if is_new and self.time_slot:
    #         self.time_slot.current_bookings += 1
    #         self.time_slot.save()
    #
    #     super().save(*args, **kwargs)

    # def calculate_total_price(self):
    #     """Calculate the total price based on the upholstery type, materials, and vehicle seats"""
    #     base_price = self.upholstery_type.base_price
    #     seats = self.seats  # Using the seats field from your Vehicle model
    #
    #     # Add the cost of the primary material for each seat
    #     material_cost = self.primary_material.price_per_seat * seats
    #
    #     # If there's an accent material, add a portion of its cost
    #     if self.accent_material:
    #         accent_cost = self.accent_material.price_per_seat * seats * decimal.Decimal(
    #             0.3)  # Assuming accent is 30% of the upholstery
    #         total = base_price + material_cost + accent_cost
    #     else:
    #         total = base_price + material_cost
    #
    #     return total


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


class CarListing(models.Model):
    FUEL_CHOICES = [
        ('gasoline', 'بنزين'),
        ('diesel', 'ديزل'),
        ('electric', 'كهربائي'),
        ('hybrid', 'هايبرد'),
    ]

    TRANSMISSION_CHOICES = [
        ('automatic', 'أوتوماتيك'),
        ('manual', 'يدوي'),
    ]

    CONDITION_CHOICES = [
        ('excellent', 'ممتازة'),
        ('good', 'جيدة'),
        ('needs_maintenance', 'تحتاج صيانة'),
    ]

    OWNER_COUNT_CHOICES = [
        (1, 'مالك واحد'),
        (2, 'مالكين'),
        (3, 'ثلاثة ملاك'),
        (4, 'أربعة ملاك أو أكثر'),
    ]

    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('active', 'نشط'),
        ('sold', 'مباع'),
        ('inactive', 'غير نشط'),
    ]

    # Basic Car Info
    brand_model = models.CharField(max_length=200, verbose_name='الماركة والطراز')
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2030)],
        verbose_name='سنة الصنع'
    )
    mileage = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='عدد الكيلومترات'
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES,
        verbose_name='نوع الوقود'
    )
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        verbose_name='ناقل الحركة'
    )
    color = models.CharField(max_length=100, verbose_name='لون السيارة')

    # Car History
    previous_accidents = models.BooleanField(verbose_name='حوادث سابقة')
    previous_owners_count = models.IntegerField(
        choices=OWNER_COUNT_CHOICES,
        verbose_name='عدد الملاك السابقين'
    )
    body_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        verbose_name='حالة الهيكل'
    )

    # Additional Details
    accessories = models.TextField(
        blank=True,
        null=True,
        help_text='قائمة الملحقات مفصولة بفواصل',
        verbose_name='الملحقات'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='السعر المطلوب'
    )

    # Contact Information
    seller_name = models.CharField(max_length=200, verbose_name='اسم البائع')
    seller_phone = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    seller_email = models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')

    # System Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='حالة الإعلان'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand_model} - {self.year}"

    @property
    def accessories_list(self):
        """Return accessories as a list"""
        if self.accessories:
            return [acc.strip() for acc in self.accessories.split(',') if acc.strip()]
        return []


class CarImage(models.Model):
    car_listing = models.ForeignKey(
        CarListing,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='car_images/%Y/%m/%d/',
        verbose_name='صورة السيارة'
    )

    class Meta:
        verbose_name = "Car Image"
        verbose_name_plural = "Car Images"

    def __str__(self):
        return f"صورة {self.car_listing.brand_model}"
