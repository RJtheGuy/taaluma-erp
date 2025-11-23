from django.contrib import admin
from .models import Warehouse, Product, Stock


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'location']


class StockInline(admin.TabularInline):
    """Display stock levels inline with products"""
    model = Stock
    extra = 1
    fields = ['warehouse', 'quantity', 'reorder_level']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']
    inlines = [StockInline]  # Show stock levels on product page


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'reorder_level']
    list_filter = ['warehouse']
    search_fields = ['product__name', 'warehouse__name']

