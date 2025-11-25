# sales/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Customer Admin - global visibility (customers can order from any location)"""
    
    list_display = ['name', 'email', 'phone', 'order_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone', 'address', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_count(self, obj):
        """Display number of orders"""
        count = obj.orders.count()
        if count > 0:
            return format_html(
                '<span style="color: #0066cc;">{} orders</span>',
                count
            )
        return '-'
    order_count.short_description = 'Orders'


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        if obj.pk and obj.quantity and obj.price:
            return format_html(
                '<strong>€{:.2f}</strong>',
                obj.quantity * obj.price
            )
        return '-'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order Admin with warehouse-based filtering and stock management"""
    
    list_display = [
        'order_number',
        'customer',
        'warehouse_display',
        'status_display',
        'total_display',
        'items_count',
        'created_at'
    ]
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    readonly_fields = ['order_number', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'warehouse', 'status')
        }),
        ('Financial', {
            'fields': ('total',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warehouse_display(self, obj):
        """Display warehouse with color coding"""
        if obj.warehouse:
            return format_html(
                '<span style="color: #0066cc; font-weight: bold;">{}</span>',
                obj.warehouse.name
            )
        return '-'
    warehouse_display.short_description = 'Location'
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#ff6600',
            'confirmed': '#0066cc',
            'shipped': '#9966ff',
            'delivered': '#00aa00',
            'cancelled': '#cc0000',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def total_display(self, obj):
        """Display total with currency formatting"""
        return format_html(
            '<strong>€{:.2f}</strong>',
            obj.total or 0
        )
    total_display.short_description = 'Total'
    
    def items_count(self, obj):
        """Display number of items"""
        count = obj.items.count()
        return format_html(
            '<span style="color: #666;">{} items</span>',
            count
        )
    items_count.short_description = 'Items'
    
    def get_queryset(self, request):
        """Filter orders based on user's warehouse assignment"""
        qs = super().get_queryset(request)
        
        # Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # Users with assigned warehouse see only their warehouse's orders
        if request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        # Users without assignment see everything
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Pre-select warehouse for assigned users"""
        if db_field.name == "warehouse":
            # If user has assigned warehouse, pre-select it and limit choices
            if request.user.assigned_warehouse and not request.user.is_superuser:
                kwargs["initial"] = request.user.assigned_warehouse.id
                kwargs["queryset"] = Warehouse.objects.filter(
                    id=request.user.assigned_warehouse.id
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Save order and track status changes"""
        # Auto-assign warehouse if user has one
        if not obj.warehouse and request.user.assigned_warehouse:
            obj.warehouse = request.user.assigned_warehouse
        
        # Track if this is a new order
        obj._is_new_order = obj.pk is None
        
        # Track old status for change detection
        if change:
            try:
                old_order = Order.objects.get(pk=obj.pk)
                obj._old_status = old_order.status
            except Order.DoesNotExist:
                obj._old_status = None
        else:
            obj._old_status = None
        
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Save order items and handle stock deduction"""
        # Save all order items
        instances = formset.save(commit=True)
        
        order = form.instance
        
        # Recalculate total
        order.calculate_total()
        
        # Handle stock based on status
        new_status = order.status
        old_status = getattr(order, '_old_status', None)
        is_new = getattr(order, '_is_new_order', False)
        
        # CASE 1: New order created as Confirmed/Shipped/Delivered
        if is_new and new_status in ['confirmed', 'shipped', 'delivered']:
            order.deduct_stock()
            self.message_user(
                request,
                format_html(
                    '✅ Order <strong>{}</strong> created and stock deducted from {}',
                    order.order_number,
                    order.warehouse.name
                ),
                level='success'
            )
        
        # CASE 2: Status changed FROM Pending TO Confirmed/Shipped/Delivered
        elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
            order.deduct_stock()
            self.message_user(
                request,
                format_html(
                    '✅ Order <strong>{}</strong> confirmed - stock deducted from {}',
                    order.order_number,
                    order.warehouse.name
                ),
                level='success'
            )
        
        # CASE 3: Status changed TO Cancelled
        elif change and old_status != 'cancelled' and new_status == 'cancelled':
            order.restore_stock()
            self.message_user(
                request,
                format_html(
                    '⚠️ Order <strong>{}</strong> cancelled - stock restored to {}',
                    order.order_number,
                    order.warehouse.name
                ),
                level='warning'
            )
        
        # CASE 4: Pending order (no stock action)
        elif new_status == 'pending':
            self.message_user(
                request,
                format_html(
                    'ℹ️ Order <strong>{}</strong> saved as Pending - stock will be deducted when confirmed',
                    order.order_number
                ),
                level='info'
            )
    
    def has_change_permission(self, request, obj=None):
        """Check if user can change this order"""
        if not super().has_change_permission(request, obj):
            return False
        
        # Superusers can change anything
        if request.user.is_superuser:
            return True
        
        # Check warehouse access
        if obj and obj.warehouse:
            return request.user.has_warehouse_access(obj.warehouse)
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Check if user can delete this order"""
        if not super().has_delete_permission(request, obj):
            return False
        
        # Superusers can delete anything
        if request.user.is_superuser:
            return True
        
        # Check warehouse access
        if obj and obj.warehouse:
            return request.user.has_warehouse_access(obj.warehouse)
        
        return True


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order Item Admin - usually accessed via Order inline"""
    
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal_display']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    readonly_fields = ['subtotal_display', 'created_at', 'updated_at']
    
    def subtotal_display(self, obj):
        """Display subtotal"""
        if obj.quantity and obj.price:
            return format_html(
                '<strong>€{:.2f}</strong>',
                obj.quantity * obj.price
            )
        return '-'
    subtotal_display.short_description = 'Subtotal'
    
    def get_queryset(self, request):
        """Filter order items based on warehouse"""
        qs = super().get_queryset(request)
        
        # Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # Filter by orders from accessible warehouses
        if request.user.assigned_warehouse:
            return qs.filter(order__warehouse=request.user.assigned_warehouse)
        
        return qs
