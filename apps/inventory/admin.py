from django.contrib import admin
from .models import Product, Warehouse, Stock

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'selling_price', 'cost_price', 'category', 'is_active']  # Fixed!
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'warehouse', 'quantity', 'reorder_level']
    list_filter = ['warehouse']
    search_fields = ['product__name', 'warehouse__name']
