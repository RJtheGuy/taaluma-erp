# inventory/admin.py
from django.contrib import admin
from .models import Warehouse, Product, Stock


class LocationFilteredAdmin(admin.ModelAdmin):
    """Base admin with location filtering"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        accessible_warehouses = request.user.get_accessible_warehouses()
        
        if hasattr(self.model, 'warehouse'):
            return qs.filter(warehouse__in=accessible_warehouses)
        elif self.model.__name__ == 'Warehouse':
            return accessible_warehouses
        else:
            if request.user.groups.filter(name__in=[
                "STORE MANAGER (Location-specific)",
                "STORE STAFF (Order entry)"
            ]).exists() and request.user.assigned_warehouse:
                return qs.filter(stocks__warehouse=request.user.assigned_warehouse).distinct()
            else:
                return qs


@admin.register(Warehouse)
class WarehouseAdmin(LocationFilteredAdmin):
    list_display = ['name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Warehouse Information', {
            'fields': ('name', 'location', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(LocationFilteredAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'sku', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Stock)
class StockAdmin(LocationFilteredAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reorder_level', 'updated_at']
    list_filter = ['warehouse', 'updated_at']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('product', 'warehouse', 'quantity', 'reorder_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "warehouse":
            kwargs["queryset"] = request.user.get_accessible_warehouses()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        if obj and not request.user.can_access_warehouse(obj.warehouse):
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        if obj and not request.user.can_access_warehouse(obj.warehouse):
            return False
        return True
