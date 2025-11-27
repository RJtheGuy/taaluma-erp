# # sales/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from .models import Customer, Order, OrderItem


# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
#     list_filter = ['is_active']
#     search_fields = ['name', 'email', 'phone']


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1
#     fields = ['product', 'quantity', 'price', 'subtotal']
#     readonly_fields = ['subtotal']
    
#     def has_change_permission(self, request, obj=None):
#         """Prevent editing items on confirmed/shipped/delivered orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_change_permission(request, obj)
    
#     def has_delete_permission(self, request, obj=None):
#         """Prevent deleting items on confirmed/shipped/delivered orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_delete_permission(request, obj)


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'customer', 'warehouse', 'total', 'status', 'created_at']
#     list_filter = ['status', 'warehouse', 'created_at']
#     search_fields = ['customer__name', 'id']
#     inlines = [OrderItemInline]
    
#     def get_readonly_fields(self, request, obj=None):
#         """Make all fields read-only for confirmed/shipped/delivered orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return ['customer', 'warehouse', 'status', 'notes', 'total']
#         return ['total']
    
#     def get_fieldsets(self, request, obj=None):
#         """Show warning message for confirmed orders"""
#         fieldsets = [
#             ('Order Information', {
#                 'fields': ('customer', 'warehouse', 'status', 'notes')
#             }),
#             ('Financial', {
#                 'fields': ('total',)
#             }),
#         ]
        
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             fieldsets.insert(0, (
#                 None, {
#                     'fields': (),
#                     'description': format_html(
#                         '<div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px;">'
#                         '<strong>⚠️ ORDER LOCKED</strong><br>'
#                         'This order is <strong>{}</strong> and cannot be modified. '
#                         'Stock has already been deducted. '
#                         'You can only <strong>delete</strong> this order (stock will be restored).'
#                         '</div>',
#                         obj.get_status_display()
#                     )
#                 }
#             ))
        
#         return fieldsets
    
#     def has_change_permission(self, request, obj=None):
#         """Allow viewing but prevent editing confirmed/shipped/delivered orders"""
#         # Always allow viewing (returning True allows access to change page)
#         return super().has_change_permission(request, obj)
    
#     def has_delete_permission(self, request, obj=None):
#         """Allow deletion of confirmed orders (stock will be restored)"""
#         if not super().has_delete_permission(request, obj):
#             return False
        
#         # Check warehouse access
#         if obj and obj.warehouse:
#             if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
#                 if obj.warehouse != request.user.assigned_warehouse:
#                     return False
        
#         return True
    
#     def delete_model(self, request, obj):
#         """When deleting order, restore stock if it was confirmed"""
#         if obj.status in ['confirmed', 'shipped', 'delivered']:
#             if obj.warehouse:
#                 obj.restore_stock()
#                 self.message_user(
#                     request,
#                     f'✅ Order deleted and stock restored to {obj.warehouse.name}',
#                     level='success'
#                 )
        
#         super().delete_model(request, obj)
    
#     def delete_queryset(self, request, queryset):
#         """Bulk delete - restore stock for all confirmed orders"""
#         for obj in queryset:
#             if obj.status in ['confirmed', 'shipped', 'delivered'] and obj.warehouse:
#                 obj.restore_stock()
        
#         count = queryset.count()
#         queryset.delete()
        
#         self.message_user(
#             request,
#             f'✅ Deleted {count} orders and restored stock where applicable',
#             level='success'
#         )
    
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
        
#         if request.user.is_superuser:
#             return qs
        
#         if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
#             return qs.filter(warehouse=request.user.assigned_warehouse)
        
#         return qs
    
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "warehouse":
#             if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
#                 kwargs["initial"] = request.user.assigned_warehouse.id
#                 from apps.inventory.models import Warehouse
#                 kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
#     def save_model(self, request, obj, form, change):
#         # Block saving if order is already confirmed/shipped/delivered
#         if change and obj.pk:
#             try:
#                 old_order = Order.objects.get(pk=obj.pk)
#                 if old_order.status in ['confirmed', 'shipped', 'delivered']:
#                     self.message_user(
#                         request,
#                         '❌ Cannot modify confirmed/shipped/delivered orders. Delete and recreate if needed.',
#                         level='error'
#                     )
#                     return  # Don't save
#             except Order.DoesNotExist:
#                 pass
        
#         if not obj.warehouse and hasattr(request.user, 'assigned_warehouse'):
#             obj.warehouse = request.user.assigned_warehouse
        
#         obj._is_new_order = obj.pk is None
        
#         if change:
#             try:
#                 old_order = Order.objects.get(pk=obj.pk)
#                 obj._old_status = old_order.status
#             except Order.DoesNotExist:
#                 obj._old_status = None
#         else:
#             obj._old_status = None
        
#         super().save_model(request, obj, form, change)
    
#     def save_formset(self, request, form, formset, change):
#         order = form.instance
        
#         # Block if order is confirmed/shipped/delivered
#         if order.status in ['confirmed', 'shipped', 'delivered'] and change:
#             self.message_user(
#                 request,
#                 '❌ Cannot modify items on confirmed orders',
#                 level='error'
#             )
#             return
        
#         instances = formset.save(commit=True)
        
#         order.calculate_total()
        
#         new_status = order.status
#         old_status = getattr(order, '_old_status', None)
#         is_new = getattr(order, '_is_new_order', False)
        
#         # New order as confirmed/shipped/delivered
#         if is_new and new_status in ['confirmed', 'shipped', 'delivered']:
#             if order.warehouse:
#                 order.deduct_stock()
#                 self.message_user(request, f'✅ Order created and stock deducted from {order.warehouse.name}', level='success')
#             else:
#                 self.message_user(request, '⚠️ No warehouse - stock NOT deducted', level='warning')
        
#         # Pending to confirmed/shipped/delivered
#         elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
#             if order.warehouse:
#                 order.deduct_stock()
#                 self.message_user(request, f'✅ Order confirmed - stock deducted from {order.warehouse.name}', level='success')
#             else:
#                 self.message_user(request, '⚠️ No warehouse assigned!', level='error')
        
#         # To cancelled
#         elif change and old_status != 'cancelled' and new_status == 'cancelled':
#             if order.warehouse:
#                 order.restore_stock()
#                 self.message_user(request, f'🔄 Order cancelled - stock restored to {order.warehouse.name}', level='warning')
        
#         # Pending
#         elif new_status == 'pending':
#             self.message_user(request, 'ℹ️ Order saved as Pending - stock will be deducted when confirmed', level='info')


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['order', 'product', 'quantity', 'price', 'subtotal']
#     list_filter = ['order__status', 'created_at']
#     search_fields = ['order__id', 'product__name']
#     readonly_fields = ['subtotal']

# apps/sales/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Order, OrderItem, Customer


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id_short',
        'customer',
        'warehouse',
        'total',
        'status_display',
        'created_at'
    ]
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'id']
    readonly_fields = ['total', 'created_at', 'updated_at']  # ← FIXED!
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'warehouse', 'status')
        }),
        ('Totals', {
            'fields': ('total',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at'),  # ← FIXED!
            'classes': ('collapse',)
        }),
    )
    
    def order_id_short(self, obj):
        return str(obj.id)[:8]
    order_id_short.short_description = 'Order ID'
    
    def total_display(self, obj):
        return format_html(
            '<strong style="color: #2e7d32;">€{:.2f}</strong>',
            obj.total
        )
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def status_display(self, obj):
        colors = {
            'pending': '#ff9800',
            'confirmed': '#2196f3',
            'shipped': '#9c27b0',
            'delivered': '#4caf50',
            'cancelled': '#f44336',
        }
        
        icons = {
            'pending': '⏳',
            'confirmed': '✅',
            'shipped': '📦',
            'delivered': '🎉',
            'cancelled': '❌',
        }
        
        color = colors.get(obj.status, '#757575')
        icon = icons.get(obj.status, '•')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_status_display().upper()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def save_model(self, request, obj, form, change):
        """
        Custom save with user-aware validation
        Passes the user to model's save method for permission checking
        """
        try:
            # If order is being confirmed, check stock first
            if obj.status == 'confirmed' and (not change or form.initial.get('status') != 'confirmed'):
                # Pass the request.user to the save method
                obj.save(user=request.user)
                
                # Deduct stock
                obj.deduct_stock()
                
                messages.success(
                    request,
                    f'✅ Order created and stock deducted from {obj.warehouse.name}'
                )
            else:
                # Pass the user for tracking
                obj.save(user=request.user)
        
        except Exception as e:
            # Show the error message
            messages.error(request, str(e))
            raise
    
    def delete_model(self, request, obj):
        """Restore stock when deleting order"""
        if obj.status == 'confirmed':
            obj.restore_stock()
            messages.success(
                request,
                f'✅ Order deleted and stock restored to {obj.warehouse.name}'
            )
        
        super().delete_model(request, obj)
    
    def get_queryset(self, request):
        """Filter orders based on user permissions"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit warehouse choices based on user permissions"""
        if db_field.name == "warehouse":
            if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                from apps.inventory.models import Warehouse
                kwargs["queryset"] = Warehouse.objects.filter(
                    id=request.user.assigned_warehouse.id
                )
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at']
