from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role', 'assigned_warehouse')}),  # Added assigned_warehouse here
    )
    list_display = ['username', 'email', 'role', 'assigned_warehouse', 'is_staff']  # Added assigned_warehouse here
    list_filter = ['role', 'is_staff', 'is_superuser', 'assigned_warehouse']  # Added assigned_warehouse here
