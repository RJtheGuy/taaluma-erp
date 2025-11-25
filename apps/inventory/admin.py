from django.contrib import admin
from .models import Warehouse, Product, Stock


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'location']
    
    # ADD THIS METHOD:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(id=request.user.assigned_warehouse.id)
        
        return qs


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # KEEP YOUR EXACT FIELDS - don't change them!
    list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']
    
    # Products are global - no filtering needed


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    # KEEP YOUR EXACT FIELDS
    list_display = ['product', 'warehouse', 'quantity', 'reorder_level']
    list_filter = ['warehouse']
    search_fields = ['product__name', 'warehouse__name']
    
    # ADD THIS METHOD:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        return qs
    
    # ADD THIS METHOD:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "warehouse":
            if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
