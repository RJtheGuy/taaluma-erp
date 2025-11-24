# sales/admin.py
from django.contrib import admin
from .models import Customer, Order, OrderItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total', 'status', 'created_at']  # Removed 'warehouse'
    list_filter = ['status', 'created_at']  # Removed 'warehouse'
    search_fields = ['customer__name', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['total']
    
    # Removed get_queryset - no warehouse filter needed since Order doesn't have warehouse field
    # If you want to filter by warehouse, you'd need to add a warehouse field to your Order model
    
    # Removed formfield_for_foreignkey - no warehouse field to pre-select
    
    def save_model(self, request, obj, form, change):
        """Save the order - stock deduction happens in save_formset"""
        obj._is_new_order = obj.pk is None
        
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
        """Save the inline items and then handle stock + total calculation"""
        instances = formset.save(commit=True)
        
        order = form.instance
        order.calculate_total()
        
        if hasattr(order, '_is_new_order') and order._is_new_order:
            if order.status in ['confirmed', 'shipped', 'delivered']:
                order.deduct_stock()
                self.message_user(
                    request,
                    f"Order created and stock deducted for {order.items.count()} items.",
                    level='success'
                )
        elif hasattr(order, '_old_status'):
            if order._old_status != 'cancelled' and order.status == 'cancelled':
                order.restore_stock()
                self.message_user(
                    request,
                    "Order cancelled and stock restored.",
                    level='warning'
                )
            elif order._old_status == 'pending' and order.status in ['confirmed', 'shipped', 'delivered']:
                order.deduct_stock()
                self.message_user(
                    request,
                    f"Order confirmed and stock deducted.",
                    level='success'
                )
