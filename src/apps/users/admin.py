# Register your models here.
# yourapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


# Unregister the default User admin to customize it


# Custom Permission Admin
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type', 'app_label')
    list_filter = ('content_type__app_label', 'content_type')
    search_fields = ('name', 'codename', 'content_type__model')
    ordering = ('content_type__app_label', 'content_type', 'codename')

    def app_label(self, obj):
        return obj.content_type.app_label

    app_label.short_description = 'App Label'
    app_label.admin_order_field = 'content_type__app_label'


# Custom Content Type Admin
@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model', 'name', 'id')
    list_filter = ('app_label',)
    search_fields = ('app_label', 'model')
    ordering = ('app_label', 'model')
    readonly_fields = ('id',)

    # Add custom actions
    actions = ['show_permissions']

    def show_permissions(self, request, queryset):
        """Custom action to show all permissions for selected content types"""
        for content_type in queryset:
            permissions = Permission.objects.filter(content_type=content_type)
            self.message_user(
                request,
                f"Content Type: {content_type} has {permissions.count()} permissions"
            )

    show_permissions.short_description = "Show permission count for selected content types"


# Enhanced Group Admin
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

    def permission_count(self, obj):
        return obj.permissions.count()

    permission_count.short_description = 'Permission Count'


# Re-register Group with custom admin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


# Enhanced User Admin with better permission display
class UserAdmin(BaseUserAdmin):
    # Add custom fields to the user admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Permissions', {
            'fields': ('user_permissions', 'groups'),
            'classes': ('collapse',)
        }),
    )

    # Add permission info to list display
    list_display = BaseUserAdmin.list_display + ('permission_count', 'group_count')

    def permission_count(self, obj):
        return obj.user_permissions.count()

    permission_count.short_description = 'Direct Permissions'

    def group_count(self, obj):
        return obj.groups.count()

    group_count.short_description = 'Groups'


# Register the enhanced User admin
admin.site.register(User, UserAdmin)


# Custom admin for viewing all permissions by app
class PermissionsByAppAdmin(admin.ModelAdmin):
    """A read-only view to see permissions organized by app"""
    list_display = ('app_label', 'model', 'permission_name', 'permission_codename')
    list_filter = ('content_type__app_label',)
    search_fields = ('name', 'codename')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def app_label(self, obj):
        return obj.content_type.app_label

    app_label.short_description = 'App'

    def model(self, obj):
        return obj.content_type.model

    model.short_description = 'Model'

    def permission_name(self, obj):
        return obj.name

    permission_name.short_description = 'Permission Name'

    def permission_codename(self, obj):
        return obj.codename

    permission_codename.short_description = 'Code Name'


# Create a proxy model for the read-only permission view
class PermissionProxy(Permission):
    class Meta:
        proxy = True
        verbose_name = 'Permission Overview'
        verbose_name_plural = 'Permissions Overview'


admin.site.register(PermissionProxy, PermissionsByAppAdmin)
