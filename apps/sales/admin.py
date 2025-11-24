from django.contrib import admin
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Changed from 0 to 1 for easier item adding
    fields = ['product', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['total']  # Make total readonly since it's calculated
    
    def save_model(self, request, obj, form, change):
        """Save the order - stock deduction happens in save_formset"""
        # Track if this is a new order
        obj._is_new_order = obj.pk is None
        
        # Track old status for cancelled orders
        if change:
            try:
                old_order = Order.objects.get(pk=obj.pk)
                obj._old_status = old_order.status
            except Order.DoesNotExist:
                obj._old_status = None
        else:
            obj._old_status = None
        
        # Save the order
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Save the inline items and then handle stock + total calculation"""
        # Save all the order items
        instances = formset.save(commit=True)
        
        order = form.instance
        
        # Now that items are saved, calculate total
        order.calculate_total()
        
        # Handle stock deduction/restoration
        if hasattr(order, '_is_new_order') and order._is_new_order:
            # New order - deduct stock if status requires it
            if order.status in ['confirmed', 'shipped', 'delivered']:
                order.deduct_stock()
                self.message_user(
                    request,
                    f"Order created and stock deducted for {order.items.count()} items.",
                    level='success'
                )
        elif hasattr(order, '_old_status'):
            # Existing order - check for status changes
            if order._old_status != 'cancelled' and order.status == 'cancelled':
                # Order was just cancelled - restore stock
                order.restore_stock()
                self.message_user(
                    request,
                    "Order cancelled and stock restored.",
                    level='warning'
                )
            elif order._old_status == 'pending' and order.status in ['confirmed', 'shipped', 'delivered']:
                # Order was just confirmed - deduct stock now
                order.deduct_stock()
                self.message_user(
                    request,
                    f"Order confirmed and stock deducted.",
                    level='success'
                )
