from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Brand, VehicleType, Feature, Vehicle, VehicleImage, InquiryData


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'vehicle_count', 'description_short')
    search_fields = ('name', 'description')
    readonly_fields = ('logo_preview_large', 'vehicle_count')
    ordering = ('name',)

    fieldsets = (
        ('Brand Information', {
            'fields': ('name', 'description')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview_large')
        }),
        ('Statistics', {
            'fields': ('vehicle_count',),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: contain;">', obj.logo.url)
        return "No Logo"

    logo_preview.short_description = 'Logo'

    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;">',
                               obj.logo.url)
        return "No Logo"

    logo_preview_large.short_description = 'Logo Preview'

    def vehicle_count(self, obj):
        count = obj.vehicles.count()
        if count > 0:
            url = reverse('admin:vehicles_vehicle_changelist') + f'?brand__id__exact={obj.id}'
            return format_html('<a href="{}">{} vehicles</a>', url, count)
        return "0 vehicles"

    vehicle_count.short_description = 'Total Vehicles'

    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "No description"

    description_short.short_description = 'Description'


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_count')
    search_fields = ('name',)
    ordering = ('name',)

    def vehicle_count(self, obj):
        count = obj.vehicles.count()
        if count > 0:
            url = reverse('admin:vehicles_vehicle_changelist') + f'?features__id__exact={obj.id}'
            return format_html('<a href="{}">{} vehicles</a>', url, count)
        return "0 vehicles"

    vehicle_count.short_description = 'Used in Vehicles'


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview', 'is_primary', 'caption')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 75px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'vehicle_info', 'brand', 'year', 'price_display', 'condition',
        'mileage_display', 'status_indicators', 'primary_image_preview', 'created_at'
    )
    list_filter = (
        'brand', 'year', 'condition', 'engine_type', 'transmission',
        'is_featured', 'is_active', 'contract_type', 'created_at'
    )
    search_fields = ('model', 'brand__name', 'color', 'body_type')
    readonly_fields = (
        'created_at', 'updated_at', 'vehicle_images_preview',
        'features_display', 'inquiry_info'
    )
    filter_horizontal = ('features',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [VehicleImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'model', 'year', 'price', 'currency')
        }),
        ('Vehicle Details', {
            'fields': ('body_type', 'color', 'mileage', 'condition')
        }),
        ('Technical Specifications', {
            'fields': (
                'engine_type', 'engine_capacity', 'cylinders',
                'transmission', 'seats'
            )
        }),
        ('Features', {
            'fields': ('features', 'features_display'),
            'classes': ('collapse',)
        }),
        ('Status & Settings', {
            'fields': (
                'is_active', 'is_featured', 'is_negotiable', 'contract_type'
            )
        }),
        ('Insurance & Registration', {
            'fields': ('insurance_expiry',),
            'classes': ('collapse',)
        }),
        ('Inquiry Information', {
            'fields': ('inquiry_data', 'inquiry_info'),
            'classes': ('collapse',)
        }),
        ('Vehicle Images', {
            'fields': ('vehicle_images_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Custom actions
    actions = [
        'mark_as_featured', 'unmark_as_featured', 'mark_as_active',
        'mark_as_inactive', 'mark_contract_type', 'unmark_contract_type'
    ]

    def vehicle_info(self, obj):
        return f"{obj.brand} {obj.model}"

    vehicle_info.short_description = 'Vehicle'
    vehicle_info.admin_order_field = 'model'

    def price_display(self, obj):
        return f"{obj.price} {obj.currency}"

    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def mileage_display(self, obj):
        return f"{obj.mileage:,} KM"

    mileage_display.short_description = 'Mileage'
    mileage_display.admin_order_field = 'mileage'

    def status_indicators(self, obj):
        indicators = []
        if obj.is_featured:
            indicators.append(
                '<span style="background: #ffc107; color: #000; padding: 2px 6px; border-radius: 3px; font-size: 11px;">FEATURED</span>')
        if obj.contract_type:
            indicators.append(
                '<span style="background: #17a2b8; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 11px;">RENT</span>')
        if obj.is_negotiable:
            indicators.append(
                '<span style="background: #28a745; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 11px;">NEGO</span>')
        if not obj.is_active:
            indicators.append(
                '<span style="background: #dc3545; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 11px;">INACTIVE</span>')

        return format_html(' '.join(indicators)) if indicators else '-'

    status_indicators.short_description = 'Status'

    def primary_image_preview(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            return format_html('<img src="{}" style="width: 60px; height: 45px; object-fit: cover;">',
                               primary_image.image.url)
        elif obj.images.exists():
            first_image = obj.images.first()
            return format_html('<img src="{}" style="width: 60px; height: 45px; object-fit: cover;">',
                               first_image.image.url)
        return "No Image"

    primary_image_preview.short_description = 'Image'

    def vehicle_images_preview(self, obj):
        if obj.pk:
            images = obj.images.all()[:6]  # Show first 6 images
            html = ""
            for img in images:
                primary_badge = ' <span style="background: #007cba; color: #fff; padding: 1px 4px; border-radius: 2px; font-size: 10px;">PRIMARY</span>' if img.is_primary else ''
                html += f'<div style="display: inline-block; margin: 5px; text-align: center;"><img src="{img.image.url}" style="width: 120px; height: 90px; object-fit: cover;"><br><small>{img.caption or "No caption"}{primary_badge}</small></div>'
            if obj.images.count() > 6:
                html += f'<div style="margin: 5px;"><small>... and {obj.images.count() - 6} more images</small></div>'
            return mark_safe(html) if html else "No images"
        return "Save vehicle first to add images"

    vehicle_images_preview.short_description = 'Vehicle Images'

    def features_display(self, obj):
        if obj.pk:
            features = obj.features.all()
            if features:
                feature_list = ', '.join([f.name for f in features])
                return feature_list
            return "No features selected"
        return "Save vehicle first to select features"

    features_display.short_description = 'Selected Features'

    def inquiry_info(self, obj):
        if obj.inquiry_data:
            return format_html(
                'Phone: {}<br>WhatsApp: {}',
                obj.inquiry_data.phone,
                obj.inquiry_data.whatsapp
            )
        return "No inquiry data"

    inquiry_info.short_description = 'Inquiry Contact'

    # Custom actions
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} vehicle(s) marked as featured.')

    mark_as_featured.short_description = 'Mark selected vehicles as featured'

    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} vehicle(s) unmarked as featured.')

    unmark_as_featured.short_description = 'Unmark selected vehicles as featured'

    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} vehicle(s) marked as active.')

    mark_as_active.short_description = 'Mark selected vehicles as active'

    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} vehicle(s) marked as inactive.')

    mark_as_inactive.short_description = 'Mark selected vehicles as inactive'

    def mark_contract_type(self, request, queryset):
        updated = queryset.update(contract_type=True)
        self.message_user(request, f'{updated} vehicle(s) marked for rent.')

    mark_contract_type.short_description = 'Mark selected vehicles for rent'

    def unmark_contract_type(self, request, queryset):
        updated = queryset.update(contract_type=False)
        self.message_user(request, f'{updated} vehicle(s) unmarked for rent.')

    unmark_contract_type.short_description = 'Unmark selected vehicles for rent'

    # Override get_queryset for better performance
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand', 'inquiry_data').prefetch_related('images',
                                                                                                      'features')


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'image_preview', 'is_primary', 'caption')
    list_filter = ('is_primary', 'vehicle__brand')
    search_fields = ('vehicle__model', 'vehicle__brand__name', 'caption')
    readonly_fields = ('image_preview_large',)

    fieldsets = (
        ('Image Information', {
            'fields': ('vehicle', 'is_primary', 'caption')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 45px; object-fit: cover;">', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 400px; max-height: 300px; object-fit: contain;">',
                               obj.image.url)
        return "No Image"

    image_preview_large.short_description = 'Image Preview'

    # Override get_queryset for better performance
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vehicle', 'vehicle__brand')


@admin.register(InquiryData)
class InquiryDataAdmin(admin.ModelAdmin):
    list_display = ('phone', 'whatsapp', 'vehicle_count')
    search_fields = ('phone', 'whatsapp')
    readonly_fields = ('vehicle_list',)

    fieldsets = (
        ('Contact Information', {
            'fields': ('phone', 'whatsapp')
        }),
        ('Associated Vehicles', {
            'fields': ('vehicle_list',),
            'classes': ('collapse',)
        }),
    )

    def vehicle_count(self, obj):
        count = obj.vehicles.count()
        if count > 0:
            url = reverse('admin:vehicles_vehicle_changelist') + f'?inquiry_data__id__exact={obj.id}'
            return format_html('<a href="{}">{} vehicles</a>', url, count)
        return "0 vehicles"

    vehicle_count.short_description = 'Associated Vehicles'

    def vehicle_list(self, obj):
        if obj.pk:
            vehicles = obj.vehicles.all()
            if vehicles:
                vehicle_links = []
                for vehicle in vehicles:
                    url = reverse('admin:vehicles_vehicle_change', args=[vehicle.id])
                    vehicle_links.append(f'<a href="{url}">{vehicle}</a>')
                return format_html('<br>'.join(vehicle_links))
            return "No vehicles associated"
        return "Save inquiry first to see associated vehicles"

    vehicle_list.short_description = 'Vehicle List'
