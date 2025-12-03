# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User


# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Additional Info', {'fields': ('phone', 'role', 'assigned_warehouse')}),  # Added assigned_warehouse here
#     )
#     list_display = ['username', 'email', 'role', 'assigned_warehouse', 'is_staff']  # Added assigned_warehouse here
#     list_filter = ['role', 'is_staff', 'is_superuser', 'assigned_warehouse']  # Added assigned_warehouse here

# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'subscription_status_display', 
        'warehouse_count', 
        'user_count',
        'monthly_fee',
        'is_active',
        'created_at'
    ]
    list_filter = ['subscription_status', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'contact_email']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Subscription & Billing', {
            'fields': ('subscription_status', 'monthly_fee', 'trial_end_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = []
    
    def subscription_status_display(self, obj):
        colors = {
            'trial': '#ff9800',
            'active': '#4caf50',
            'suspended': '#f44336',
            'cancelled': '#9e9e9e',
        }
        color = colors.get(obj.subscription_status, '#9e9e9e')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_subscription_status_display().upper()
        )
    subscription_status_display.short_description = 'Status'
    
    def warehouse_count(self, obj):
        count = obj.warehouse_count
        return format_html('<strong>{}</strong> warehouses', count)
    warehouse_count.short_description = 'Warehouses'
    
    def user_count(self, obj):
        count = obj.user_count
        return format_html('<strong>{}</strong> users', count)
    user_count.short_description = 'Users'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 
        'email', 
        'organization', 
        'role',
        'assigned_warehouse',
        'is_active',
        'is_staff'
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'role', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Organization & Role', {'fields': ('organization', 'role', 'assigned_warehouse')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'organization', 'role'),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_warehouse" and not request.user.is_superuser:
            if hasattr(request.user, 'organization') and request.user.organization:
                from apps.inventory.models import Warehouse
                kwargs["queryset"] = Warehouse.objects.filter(
                    organization=request.user.organization
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
