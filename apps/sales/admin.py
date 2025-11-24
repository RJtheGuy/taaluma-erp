# sales/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Order, OrderItem


class LocationFilteredSalesAdmin(admin.ModelAdmin):
    """Base admin for sales with location filtering"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        accessible_warehouses = request.user.get_accessible_warehouses()
        
        if hasattr(self.model, 'warehouse'):
            return qs.filter(warehouse__in=accessible_warehouses)
        
        if request.user.groups.filter(name__in=[
            "STORE MANAGER (Location-specific)",
            "STORE STAFF (Order entry)"
        ]).exists() and request.user.assigned_warehouse:
            if self.model.__name__ == 'Customer':
                return qs.filter(
                    orders__warehouse=request.user.assigned_warehouse
                ).distinct()
        
        return qs


@admin.register(Customer)
class CustomerAdmin(LocationFilteredSalesAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        if obj.quantity and obj.price:
            return f"€{obj.quantity * obj.price:.2f}"
        return "€0.00"


@admin.register(Order)
class OrderAdmin(LocationFilteredSalesAdmin):
    list_display = [
        'order_number',
        'customer',
        'warehouse_location',
        'status',
        'total_amount',
        'created_at'
    ]
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'warehouse', 'status')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warehouse_location(self, obj):
        if obj.warehouse:
            return format_html(
                '<span style="color: #0066cc; font-weight: bold;">{}</span>',
                obj.warehouse.name
            )
        return '-'
    warehouse_location.short_description = 'Location'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "warehouse":
            kwargs["queryset"] = request.user.get_accessible_warehouses()
            
            if request.user.groups.filter(name__in=[
                "STORE MANAGER (Location-specific)",
                "STORE STAFF (Order entry)"
            ]).exists() and request.user.assigned_warehouse:
                kwargs["initial"] = request.user.assigned_warehouse.id
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not obj.warehouse and request.user.assigned_warehouse:
            obj.warehouse = request.user.assigned_warehouse
        
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        order = form.instance
        
        old_status = None
        if change:
            try:
                old_status = Order.objects.get(pk=order.pk).status
            except Order.DoesNotExist:
                old_status = None
        
        instances = formset.save(commit=False)
        
        for instance in instances:
            instance.save()
        
        formset.save_m2m()
        
        new_status = order.status
        
        if not change and new_status in ['confirmed', 'shipped', 'delivered']:
            order.deduct_stock()
            self.message_user(
                request,
                f"Order {order.order_number} created and stock deducted from {order.warehouse.name}",
                level='success'
            )
        
        elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
            order.deduct_stock()
            self.message_user(
                request,
                f"Order {order.order_number} confirmed - stock deducted from {order.warehouse.name}",
                level='success'
            )
        
        elif change and old_status != 'cancelled' and new_status == 'cancelled':
            order.restore_stock()
            self.message_user(
                request,
                f"Order {order.order_number} cancelled - stock restored to {order.warehouse.name}",
                level='warning'
            )
        
        elif new_status == 'pending':
            self.message_user(
                request,
                f"Order {order.order_number} saved as Pending - stock will be deducted when confirmed",
                level='info'
            )
    
    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        
        if obj and obj.warehouse and not request.user.can_access_warehouse(obj.warehouse):
            return False
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        if not super().has_delete_permission(request, obj):
            return False
        
        if obj and obj.warehouse and not request.user.can_access_warehouse(obj.warehouse):
            return False
        
        return True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        accessible_warehouses = request.user.get_accessible_warehouses()
        return qs.filter(warehouse__in=accessible_warehouses)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal_display']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    readonly_fields = ['subtotal_display']
    
    def subtotal_display(self, obj):
        return f"€{obj.quantity * obj.price:.2f}"
    subtotal_display.short_description = 'Subtotal'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        accessible_warehouses = request.user.get_accessible_warehouses()
        return qs.filter(order__warehouse__in=accessible_warehouses)
