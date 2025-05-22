# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    UpholsteryMaterial, UpholsteryType, UpholsteryGalleryImage,
    ServiceLocation, ServiceTimeSlot, UpholsteryCarModels,
    UpholsteryMaterialTypes, UpholsteryBooking, BookingImage
)


@admin.register(UpholsteryMaterial)
class UpholsteryMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)
    readonly_fields = ('image_preview_large',)

    fieldsets = (
        ('Material Information', {
            'fields': ('name',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;">', obj.image.url)
        return "No Image"

    image_preview_large.short_description = 'Image Preview'


@admin.register(UpholsteryType)
class UpholsteryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'estimated_hours', 'available', 'gallery_count')
    list_filter = ('available', 'estimated_hours')
    search_fields = ('name', 'description')
    list_editable = ('available', 'base_price')

    def gallery_count(self, obj):
        return obj.gallery_images.count()

    gallery_count.short_description = 'Gallery Images'


class UpholsteryGalleryImageInline(admin.TabularInline):
    model = UpholsteryGalleryImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 75px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


@admin.register(UpholsteryGalleryImage)
class UpholsteryGalleryImageAdmin(admin.ModelAdmin):
    list_display = ('upholstery_type', 'material', 'vehicle_info', 'featured', 'image_preview')
    list_filter = ('featured', 'upholstery_type', 'material')
    search_fields = ('caption', 'vehicle_info')
    list_editable = ('featured',)
    readonly_fields = ('image_preview_large',)

    fieldsets = (
        ('Gallery Information', {
            'fields': ('upholstery_type', 'material', 'featured')
        }),
        ('Details', {
            'fields': ('caption', 'vehicle_info')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 300px;">', obj.image.url)
        return "No Image"

    image_preview_large.short_description = 'Image Preview'


@admin.register(ServiceLocation)
class ServiceLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'working_hours', 'is_active', 'available_slots_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'phone', 'email')
    list_editable = ('is_active',)

    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'address', 'phone', 'email')
        }),
        ('Working Hours', {
            'fields': ('working_hours_start', 'working_hours_end')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def working_hours(self, obj):
        return f"{obj.working_hours_start} - {obj.working_hours_end}"

    working_hours.short_description = 'Working Hours'

    def available_slots_count(self, obj):
        return obj.time_slots.filter(current_bookings__lt=models.F('max_bookings')).count()

    available_slots_count.short_description = 'Available Slots'


class ServiceTimeSlotInline(admin.TabularInline):
    model = ServiceTimeSlot
    extra = 1
    readonly_fields = ('is_available_display',)

    def is_available_display(self, obj):
        if obj.pk:
            status = "Available" if obj.is_available else "Fully Booked"
            color = "green" if obj.is_available else "red"
            return format_html('<span style="color: {};">{}</span>', color, status)
        return "-"

    is_available_display.short_description = 'Availability'


@admin.register(ServiceTimeSlot)
class ServiceTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('location', 'date', 'time_range', 'booking_status', 'is_available_display')
    list_filter = ('location', 'date')
    search_fields = ('location__name',)
    date_hierarchy = 'date'
    ordering = ('date', 'start_time')

    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"

    time_range.short_description = 'Time'

    def booking_status(self, obj):
        return f"{obj.current_bookings}/{obj.max_bookings}"

    booking_status.short_description = 'Bookings'

    def is_available_display(self, obj):
        status = "Available" if obj.is_available else "Fully Booked"
        color = "green" if obj.is_available else "red"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, status)

    is_available_display.short_description = 'Status'


@admin.register(UpholsteryCarModels)
class UpholsteryCarModelsAdmin(admin.ModelAdmin):
    list_display = ('name', 'booking_count')
    search_fields = ('name',)
    ordering = ('name',)

    def booking_count(self, obj):
        return obj.model_bookings.count()

    booking_count.short_description = 'Total Bookings'


@admin.register(UpholsteryMaterialTypes)
class UpholsteryMaterialTypesAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'booking_count')
    search_fields = ('name',)
    readonly_fields = ('image_preview_large',)
    ordering = ('name',)

    fieldsets = (
        ('Material Type Information', {
            'fields': ('name',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;">', obj.image.url)
        return "No Image"

    image_preview_large.short_description = 'Image Preview'

    def booking_count(self, obj):
        return obj.material_bookings.count()

    booking_count.short_description = 'Total Bookings'


class BookingImageInline(admin.TabularInline):
    model = BookingImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 75px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


@admin.register(UpholsteryBooking)
class UpholsteryBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user_name', 'car_model', 'primary_material', 'material_type', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'primary_material', 'material_type', 'car_model')
    search_fields = ('user__username', 'user__email', 'car_model__name', 'primary_material__name')
    readonly_fields = ('created_at', 'updated_at', 'booking_images_preview')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [BookingImageInline]

    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'status')
        }),
        ('Vehicle & Materials', {
            'fields': ('car_model', 'primary_material', 'material_type')
        }),
        ('Images', {
            'fields': ('booking_images_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    # Custom actions
    actions = ['mark_as_confirmed', 'mark_as_in_progress', 'mark_as_completed', 'mark_as_cancelled']

    def booking_id(self, obj):
        return f"Booking #{obj.id}"

    booking_id.short_description = 'Booking ID'

    def user_name(self, obj):
        if obj.user:
            return obj.user.username or obj.user.email
        return "Anonymous"

    user_name.short_description = 'Customer'

    def booking_images_preview(self, obj):
        if obj.pk:
            images = obj.images.all()[:4]  # Show first 4 images
            html = ""
            for img in images:
                status = "Before" if img.is_before else "After"
                html += f'<div style="display: inline-block; margin: 5px;"><img src="{img.image.url}" style="width: 100px; height: 75px; object-fit: cover;"><br><small>{status}</small></div>'
            if obj.images.count() > 4:
                html += f'<div style="margin: 5px;"><small>... and {obj.images.count() - 4} more images</small></div>'
            return mark_safe(html) if html else "No images"
        return "Save booking first to add images"

    booking_images_preview.short_description = 'Booking Images'

    # Custom actions
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status=UpholsteryBooking.STATUS_CONFIRMED)
        self.message_user(request, f'{updated} booking(s) marked as confirmed.')

    mark_as_confirmed.short_description = 'Mark selected bookings as confirmed'

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status=UpholsteryBooking.STATUS_IN_PROGRESS)
        self.message_user(request, f'{updated} booking(s) marked as in progress.')

    mark_as_in_progress.short_description = 'Mark selected bookings as in progress'

    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status=UpholsteryBooking.STATUS_COMPLETED,
            completed_at=timezone.now()
        )
        self.message_user(request, f'{updated} booking(s) marked as completed.')

    mark_as_completed.short_description = 'Mark selected bookings as completed'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=UpholsteryBooking.STATUS_CANCELLED)
        self.message_user(request, f'{updated} booking(s) marked as cancelled.')

    mark_as_cancelled.short_description = 'Mark selected bookings as cancelled'

    # Override get_queryset for better performance
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'primary_material', 'material_type', 'car_model')


@admin.register(BookingImage)
class BookingImageAdmin(admin.ModelAdmin):
    list_display = ('booking', 'image_type', 'caption', 'image_preview')
    list_filter = ('is_before', 'booking__status')
    search_fields = ('caption', 'booking__id')
    readonly_fields = ('image_preview_large',)

    fieldsets = (
        ('Image Information', {
            'fields': ('booking', 'is_before', 'caption')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
    )

    def image_type(self, obj):
        return "Before" if obj.is_before else "After"

    image_type.short_description = 'Type'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 300px;">', obj.image.url)
        return "No Image"

    image_preview_large.short_description = 'Image Preview'


# Add inlines to relevant models
UpholsteryTypeAdmin.inlines = [UpholsteryGalleryImageInline]
ServiceLocationAdmin.inlines = [ServiceTimeSlotInline]
