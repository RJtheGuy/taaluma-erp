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
    list_display = ['id', 'customer', 'warehouse', 'total', 'status', 'created_at']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['customer__name', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['total']
    
    def get_queryset(self, request):
        """Filter orders based on user's warehouse assignment"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Pre-select warehouse for assigned users"""
        if db_field.name == "warehouse":
            if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                kwargs["initial"] = request.user.assigned_warehouse.id
                kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
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
