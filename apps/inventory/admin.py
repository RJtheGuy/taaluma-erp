# inventory/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Warehouse, Product, Stock


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """Warehouse Admin with location-based filtering"""
    
    list_display = ['name', 'location', 'is_active', 'user_count', 'created_at']
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
    
    def user_count(self, obj):
        """Display number of users assigned to this warehouse"""
        count = obj.assigned_users.count()
        if count > 0:
            return format_html(
                '<span style="color: #0066cc;">{} users</span>',
                count
            )
        return '-'
    user_count.short_description = 'Assigned Users'
    
    def get_queryset(self, request):
        """Filter warehouses based on user's assignment"""
        qs = super().get_queryset(request)
        
        # Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # Users with assigned warehouse see only their warehouse
        if request.user.assigned_warehouse:
            return qs.filter(id=request.user.assigned_warehouse.id)
        
        # Users without assignment see everything (owners/general managers)
        return qs


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product Admin - no location filtering (products are global)"""
    
    list_display = ['name', 'sku', 'category', 'price', 'stock_info', 'created_at']
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
    
    def stock_info(self, obj):
        """Display total stock across all warehouses"""
        total = sum([stock.quantity for stock in obj.stocks.all()])
        if total > 0:
            return format_html(
                '<span style="color: #00aa00; font-weight: bold;">{} units</span>',
                total
            )
        return format_html('<span style="color: #cc0000;">Out of stock</span>')
    stock_info.short_description = 'Total Stock'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """Stock Admin with warehouse-based filtering"""
    
    list_display = [
        'product', 
        'warehouse', 
        'quantity_display', 
        'reorder_level', 
        'status',
        'updated_at'
    ]
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
    
    def quantity_display(self, obj):
        """Display quantity with color coding"""
        if obj.quantity <= 0:
            color = '#cc0000'  # Red
            text = 'OUT OF STOCK'
        elif obj.quantity <= obj.reorder_level:
            color = '#ff6600'  # Orange
            text = f'{obj.quantity} (LOW)'
        else:
            color = '#00aa00'  # Green
            text = str(obj.quantity)
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    quantity_display.short_description = 'Quantity'
    
    def status(self, obj):
        """Display stock status"""
        if obj.quantity <= 0:
            return format_html('<span style="color: #cc0000;">●</span> Out of Stock')
        elif obj.quantity <= obj.reorder_level:
            return format_html('<span style="color: #ff6600;">●</span> Low Stock')
        return format_html('<span style="color: #00aa00;">●</span> In Stock')
    status.short_description = 'Status'
    
    def get_queryset(self, request):
        """Filter stock based on user's warehouse assignment"""
        qs = super().get_queryset(request)
        
        # Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # Users with assigned warehouse see only their warehouse's stock
        if request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        # Users without assignment see everything
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter warehouse dropdown for assigned users"""
        if db_field.name == "warehouse":
            # If user has assigned warehouse, only show that one
            if request.user.assigned_warehouse and not request.user.is_superuser:
                kwargs["queryset"] = Warehouse.objects.filter(
                    id=request.user.assigned_warehouse.id
                )
                kwargs["initial"] = request.user.assigned_warehouse.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        """Check if user can change this stock record"""
        if not super().has_change_permission(request, obj):
            return False
        
        # Superusers can change anything
        if request.user.is_superuser:
            return True
        
        # Check warehouse access
        if obj:
            return request.user.has_warehouse_access(obj.warehouse)
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Check if user can delete this stock record"""
        if not super().has_delete_permission(request, obj):
            return False
        
        # Superusers can delete anything
        if request.user.is_superuser:
            return True
        
        # Check warehouse access
        if obj:
            return request.user.has_warehouse_access(obj.warehouse)
        
        return True
