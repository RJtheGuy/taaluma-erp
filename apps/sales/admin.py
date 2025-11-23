from django.contrib import admin
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name']
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        """Save the order and trigger stock deduction"""
        is_new = obj.pk is None
        old_status = None
        
        if change:  # Editing existing order
            old_status = Order.objects.get(pk=obj.pk).status
        
        super().save_model(request, obj, form, change)
        
        # After order and items are saved, calculate total and deduct stock
        if is_new and obj.status in ['pending', 'confirmed']:
            # New order - deduct stock
            obj.deduct_stock()
            obj.calculate_total()
        elif change and old_status != 'cancelled' and obj.status == 'cancelled':
            # Order cancelled - restore stock
            obj.restore_stock()
        elif change:
            # Just recalculate total for existing orders
            obj.calculate_total()
    
    def save_formset(self, request, form, formset, change):
        """Save the inline items first"""
        instances = formset.save(commit=True)
        
        # After items are saved, recalculate order total
        if form.instance.pk:
            form.instance.calculate_total()
