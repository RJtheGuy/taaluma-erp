from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal_display']
    fields = ['product', 'quantity', 'price', 'subtotal_display']
    
    def subtotal_display(self, obj):
        if obj.pk:
            return format_html('<strong>€{:.2f}</strong>', obj.subtotal)
        return '-'
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'warehouse', 'total_display', 'status', 'created_at']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['customer__name', 'id']
    readonly_fields = ['total']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'warehouse', 'status', 'notes')
        }),
        ('Financial', {
            'fields': ('total',)
        }),
    )
    
    def total_display(self, obj):
        return format_html('<strong>€{:.2f}</strong>', obj.total or 0)
    total_display.short_description = 'Total'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "warehouse":
            if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                kwargs["initial"] = request.user.assigned_warehouse.id
                kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Track order changes for stock management"""
        # Auto-assign warehouse if user has one
        if not obj.warehouse and hasattr(request.user, 'assigned_warehouse'):
            obj.warehouse = request.user.assigned_warehouse
        
        # Track if new order
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
        """Save items and handle stock deduction"""
        # Save all order items first
        instances = formset.save(commit=True)
        
        order = form.instance
        
        # Recalculate total
        order.calculate_total()
        
        # Get status info
        new_status = order.status
        old_status = getattr(order, '_old_status', None)
        is_new = getattr(order, '_is_new_order', False)
        
        # STOCK MANAGEMENT LOGIC
        
        # CASE 1: New order created as Confirmed/Shipped/Delivered
        if is_new and new_status in ['confirmed', 'shipped', 'delivered']:
            if order.warehouse:
                success = order.deduct_stock()
                if success:
                    self.message_user(
                        request,
                        format_html(
                            '✅ Order created and <strong>stock deducted</strong> from {}',
                            order.warehouse.name
                        ),
                        level='success'
                    )
                else:
                    self.message_user(
                        request,
                        '⚠️ Order created but no warehouse assigned - stock NOT deducted',
                        level='warning'
                    )
            else:
                self.message_user(
                    request,
                    '⚠️ Order created but no warehouse assigned - stock NOT deducted',
                    level='warning'
                )
        
        # CASE 2: Status changed FROM Pending TO Confirmed/Shipped/Delivered
        elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
            if order.warehouse:
                success = order.deduct_stock()
                if success:
                    self.message_user(
                        request,
                        format_html(
                            '✅ Order confirmed - <strong>stock deducted</strong> from {}',
                            order.warehouse.name
                        ),
                        level='success'
                    )
            else:
                self.message_user(
                    request,
                    '⚠️ Cannot deduct stock - no warehouse assigned!',
                    level='error'
                )
        
        # CASE 3: Status changed TO Cancelled
        elif change and old_status != 'cancelled' and new_status == 'cancelled':
            if order.warehouse:
                success = order.restore_stock()
                if success:
                    self.message_user(
                        request,
                        format_html(
                            '🔄 Order cancelled - <strong>stock restored</strong> to {}',
                            order.warehouse.name
                        ),
                        level='warning'
                    )
            else:
                self.message_user(
                    request,
                    '⚠️ Order cancelled but no warehouse was assigned',
                    level='warning'
                )
        
        # CASE 4: Pending order (no stock action)
        elif new_status == 'pending':
            self.message_user(
                request,
                'ℹ️ Order saved as Pending - stock will be deducted when confirmed',
                level='info'
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal_display']
    list_filter = ['order__status', 'created_at']
    search_fields = ['order__id', 'product__name']
    
    def subtotal_display(self, obj):
        return format_html('<strong>€{:.2f}</strong>', obj.subtotal)
    subtotal_display.short_description = 'Subtotal'
