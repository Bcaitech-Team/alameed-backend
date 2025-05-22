from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import CustomerData, Rental


@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'id_number', 'nationality', 'created_at')
    list_filter = ('nationality', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'phone_number', 'id_number')
    readonly_fields = ('created_at', 'updated_at', 'display_license_photos', 'display_id_photos')

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'phone_number', 'id_number', 'nationality')
        }),
        ('Documents', {
            'fields': ('license_front_photo', 'license_back_photo', 'id_front_photo', 'id_back_photo')
        }),
        ('Photo Preview', {
            'fields': ('display_license_photos', 'display_id_photos'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        """Display full name in list view"""
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}".strip()

    full_name.short_description = 'Full Name'

    def display_license_photos(self, obj):
        """Display license photos in admin detail view"""
        html = ""
        if obj.license_front_photo:
            html += f'<div style="margin: 10px 0;"><strong>License Front:</strong><br><img src="{obj.license_front_photo.url}" style="max-width: 300px; max-height: 200px;"></div>'
        if obj.license_back_photo:
            html += f'<div style="margin: 10px 0;"><strong>License Back:</strong><br><img src="{obj.license_back_photo.url}" style="max-width: 300px; max-height: 200px;"></div>'
        return mark_safe(html) if html else "No license photos"

    display_license_photos.short_description = 'License Photos'

    def display_id_photos(self, obj):
        """Display ID photos in admin detail view"""
        html = ""
        if obj.id_front_photo:
            html += f'<div style="margin: 10px 0;"><strong>ID Front:</strong><br><img src="{obj.id_front_photo.url}" style="max-width: 300px; max-height: 200px;"></div>'
        if obj.id_back_photo:
            html += f'<div style="margin: 10px 0;"><strong>ID Back:</strong><br><img src="{obj.id_back_photo.url}" style="max-width: 300px; max-height: 200px;"></div>'
        return mark_safe(html) if html else "No ID photos"

    display_id_photos.short_description = 'ID Photos'


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        'rental_info', 'customer_name', 'vehicle_name', 'start_date', 'end_date', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'start_date', 'end_date', 'created_at', 'vehicle__model')
    search_fields = (
        'customer_data__first_name',
        'customer_data__last_name',
        'customer_data__phone_number',
        'vehicle__make',
        'vehicle__model',
        'vehicle__license_plate'
    )
    readonly_fields = ('created_at', 'updated_at', 'calculated_total_price', 'rental_duration')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)

    fieldsets = (
        ('Rental Information', {
            'fields': ('customer_data', 'vehicle', 'user', 'status')
        }),
        ('Rental Period', {
            'fields': ('start_date', 'end_date', 'rental_duration')
        }),
        ('Pricing', {
            'fields': ('total_price', 'calculated_total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Raw ID fields for better performance with large datasets
    raw_id_fields = ('customer_data', 'vehicle', 'user')

    # Autocomplete fields (requires search_fields on related models)
    autocomplete_fields = ('customer_data', 'vehicle')

    def rental_info(self, obj):
        """Display rental ID and basic info"""
        return f"Rental #{obj.id}"

    rental_info.short_description = 'Rental'

    def customer_name(self, obj):
        """Display customer name with link to customer detail"""
        url = reverse('admin:your_app_customerdata_change', args=[obj.customer_data.id])
        return format_html('<a href="{}">{}</a>', url,
                           obj.customer_data.full_name if hasattr(obj.customer_data, 'full_name') else str(
                               obj.customer_data))

    customer_name.short_description = 'Customer'

    def vehicle_name(self, obj):
        """Display vehicle info with link to vehicle detail"""
        url = reverse('admin:vehicles_vehicle_change', args=[obj.vehicle.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.vehicle))

    vehicle_name.short_description = 'Vehicle'

    def rental_duration(self, obj):
        """Calculate and display rental duration"""
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            days = delta.days + (1 if delta.seconds > 0 else 0)
            return f"{days} day{'s' if days != 1 else ''}"
        return "Not calculated"

    rental_duration.short_description = 'Duration'

    def calculated_total_price(self, obj):
        """Show calculated total price based on vehicle rate and duration"""
        if obj.vehicle and obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            days = delta.days + (1 if delta.seconds > 0 else 0)
            calculated = obj.vehicle.price * days
            return f"${calculated:.2f} ({days} days × ${obj.vehicle.price}/day)"
        return "Cannot calculate"

    calculated_total_price.short_description = 'Calculated Price'

    # Custom actions
    actions = ['mark_as_confirmed', 'mark_as_active', 'mark_as_completed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} rental(s) marked as confirmed.')

    mark_as_confirmed.short_description = 'Mark selected rentals as confirmed'

    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} rental(s) marked as active.')

    mark_as_active.short_description = 'Mark selected rentals as active'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} rental(s) marked as completed.')

    mark_as_completed.short_description = 'Mark selected rentals as completed'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} rental(s) marked as cancelled.')

    mark_as_cancelled.short_description = 'Mark selected rentals as cancelled'

    # Override get_queryset for better performance
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer_data', 'vehicle', 'user')
