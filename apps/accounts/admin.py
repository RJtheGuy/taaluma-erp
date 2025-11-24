# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'assigned_warehouse',
        'is_active',
        'is_staff',
        'created_at'
    ]
    
    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'assigned_warehouse',
    ]
    
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Organization & Location', {
            'fields': ('organization', 'assigned_warehouse'),
            'description': 'Assign user to organization and specific location/warehouse'
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
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Organization & Location', {
            'fields': ('organization', 'assigned_warehouse')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'groups')
        }),
    )
