# inventory/admin.py
from django.contrib import admin
from .models import Warehouse, Product, Stock


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
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
    
    def get_queryset(self, request):
        """Filter warehouses based on user's assignment"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(id=request.user.assigned_warehouse.id)
        
        return qs


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
class StockAdmin(admin.ModelAdmin):
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
    
    def get_queryset(self, request):
        """Filter stock based on user's warehouse assignment"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter warehouse dropdown for assigned users"""
        if db_field.name == "warehouse":
            if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
