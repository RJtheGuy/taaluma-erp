# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with warehouse assignment support"""
    
    list_display = [
        'username',
        'email',
        'full_name',
        'assigned_warehouse_display',
        'is_active',
        'is_staff',
        'created_at'
    ]
    
    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'assigned_warehouse',
        'created_at',
    ]
    
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Warehouse Assignment', {
            'fields': ('assigned_warehouse',),
            'description': 'Assign user to a specific warehouse for location-based access control. '
                          'Leave empty for full access to all locations.'
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    add_fieldsets = (
        ('Login Credentials', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Warehouse Assignment', {
            'fields': ('assigned_warehouse',)
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'groups')
        }),
    )
    
    def assigned_warehouse_display(self, obj):
        """Display assigned warehouse with color coding"""
        if obj.assigned_warehouse:
            return format_html(
                '<span style="color: #0066cc; font-weight: bold;">{}</span>',
                obj.assigned_warehouse.name
            )
        return format_html(
            '<span style="color: #666; font-style: italic;">All Warehouses</span>'
        )
    assigned_warehouse_display.short_description = 'Location Access'
    
    def get_queryset(self, request):
        """Filter users based on requesting user's permissions"""
        qs = super().get_queryset(request)
        
        # Superusers see all users
        if request.user.is_superuser:
            return qs
        
        # Staff users see only users from their warehouse
        if request.user.assigned_warehouse:
            return qs.filter(assigned_warehouse=request.user.assigned_warehouse)
        
        # Users without assignment see all
        return qs
