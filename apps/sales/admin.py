
# # apps/sales/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.core.exceptions import ValidationError
# from django.contrib import messages
# from apps.core.admin import OrganizationFilterMixin
# from .models import Customer, Order, OrderItem

# @admin.register(Customer)
# class CustomerAdmin(OrganizationFilterMixin, admin.ModelAdmin):
#     list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
#     list_filter = ['is_active', 'created_at']
#     search_fields = ['name', 'email', 'phone']


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1
#     fields = ['product', 'quantity', 'price', 'subtotal']
#     readonly_fields = ['product', 'quantity', 'price', 'subtotal']  # Make all readonly for confirmed
    
#     def get_readonly_fields(self, request, obj=None):
#         """Make ALL fields readonly for confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return ['product', 'quantity', 'price', 'subtotal']
#         return ['subtotal']
    
#     def has_add_permission(self, request, obj=None):
#         """Prevent adding items to confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_add_permission(request, obj)
    
#     def has_change_permission(self, request, obj=None):
#         """Prevent editing items on confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_change_permission(request, obj)
    
#     def has_delete_permission(self, request, obj=None):
#         """Prevent deleting items on confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_delete_permission(request, obj)


# @admin.register(Order)
# class OrderAdmin(OrganizationFilterMixin, admin.ModelAdmin):
#     list_display = ['id', 'customer', 'warehouse', 'total', 'status', 'created_at']
#     list_filter = ['status', 'warehouse', 'created_at']
#     search_fields = ['customer__name', 'id']
#     inlines = [OrderItemInline]
    
#     def get_fields(self, request, obj=None):
#         """
#         Use different fields for confirmed orders
#         Display custom read-only fields without clickable links
#         """
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return ['customer_display', 'warehouse_display', 'status', 'notes', 'total']
#         return ['customer', 'warehouse', 'status', 'notes', 'total']
    
#     def get_readonly_fields(self, request, obj=None):
#         """Make fields read-only for confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             return ['customer_display', 'warehouse_display', 'status', 'notes', 'total']
#         return ['total']
    
#     def customer_display(self, obj):
#         """Display customer name as plain text (no clickable link)"""
#         if obj and obj.customer:
#             return format_html(
#                 '<strong>{}</strong><br>'
#                 '<small style="color: #666;">Email: {}</small><br>'
#                 '<small style="color: #666;">Phone: {}</small>',
#                 obj.customer.name,
#                 obj.customer.email or 'N/A',
#                 obj.customer.phone or 'N/A'
#             )
#         return '-'
#     customer_display.short_description = 'Customer'
    
#     def warehouse_display(self, obj):
#         """Display warehouse name as plain text (no clickable link)"""
#         if obj and obj.warehouse:
#             return format_html(
#                 '<strong>{}</strong><br>'
#                 '<small style="color: #666;">Location: {}</small>',
#                 obj.warehouse.name,
#                 obj.warehouse.location or 'N/A'
#             )
#         return '-'
#     warehouse_display.short_description = 'Warehouse'
    
#     def get_fieldsets(self, request, obj=None):
#         """Show warning message for confirmed orders"""
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             # Confirmed order - use display fields
#             fieldsets = [
#                 (None, {
#                     'fields': (),
#                     'description': format_html(
#                         '<div style="background: #fff3cd; border: 2px solid #ffc107; '
#                         'padding: 15px; border-radius: 5px; margin-bottom: 20px;">'
#                         '<strong style="color: #856404; font-size: 16px;">🔒 ORDER LOCKED</strong><br>'
#                         '<span style="color: #856404;">This order is {} and cannot be modified. '
#                         'Stock has already been deducted. '
#                         'You can only view or delete this order (stock will be restored upon deletion).</span>'
#                         '</div>',
#                         obj.get_status_display()
#                     )
#                 }),
#                 ('Order Information', {
#                     'fields': ('customer_display', 'warehouse_display', 'status', 'notes')
#                 }),
#                 ('Financial', {
#                     'fields': ('total',)
#                 }),
#             ]
#         else:
#             # Pending/cancelled order - use normal fields
#             fieldsets = [
#                 ('Order Information', {
#                     'fields': ('customer', 'warehouse', 'status', 'notes')
#                 }),
#                 ('Financial', {
#                     'fields': ('total',)
#                 }),
#             ]
        
#         return fieldsets
    
#     def has_change_permission(self, request, obj=None):
#         """
#         CRITICAL: Prevent editing confirmed orders entirely
#         Return False to disable the save buttons
#         """
#         if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#             # Allow viewing but not changing
#             return False
#         return super().has_change_permission(request, obj)
    
#     def has_delete_permission(self, request, obj=None):
#         """Allow deletion of any order (stock will be restored)"""
#         return super().has_delete_permission(request, obj)
    
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         """Override change view to allow viewing confirmed orders"""
#         extra_context = extra_context or {}
        
#         try:
#             obj = self.get_object(request, object_id)
#             if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
#                 extra_context['show_save'] = False
#                 extra_context['show_save_and_continue'] = False
#                 extra_context['show_save_and_add_another'] = False
#                 extra_context['title'] = f'View Order (Read-Only)'
#         except:
#             pass
        
#         return super().change_view(request, object_id, form_url, extra_context)
    
#     def delete_model(self, request, obj):
#         """When deleting order, restore stock if it was confirmed"""
#         if obj.status in ['confirmed', 'shipped', 'delivered']:
#             if obj.warehouse:
#                 obj.restore_stock()
#                 messages.success(
#                     request,
#                     f'✅ Order deleted and stock restored to {obj.warehouse.name}'
#                 )
        
#         super().delete_model(request, obj)
    
#     def delete_queryset(self, request, queryset):
#         """Bulk delete - restore stock for all confirmed orders"""
#         for obj in queryset:
#             if obj.status in ['confirmed', 'shipped', 'delivered'] and obj.warehouse:
#                 obj.restore_stock()
        
#         count = queryset.count()
#         queryset.delete()
        
#         messages.success(
#             request,
#             f'✅ Deleted {count} orders and restored stock where applicable'
#         )
    
#     def save_model(self, request, obj, form, change):
#         """
#         CRITICAL: Block any attempts to save confirmed orders
#         This is a safety net in case form submission bypasses permissions
#         """
#         # Check if trying to modify a confirmed order
#         if change and obj.pk:
#             try:
#                 old_order = Order.objects.get(pk=obj.pk)
#                 if old_order.status in ['confirmed', 'shipped', 'delivered']:
#                     messages.error(
#                         request,
#                         '❌ Cannot modify confirmed/shipped/delivered orders. This order is locked.'
#                     )
#                     return  # Don't save
#             except Order.DoesNotExist:
#                 pass
        
#         # Auto-assign warehouse if user has one
#         if not obj.warehouse and hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
#             obj.warehouse = request.user.assigned_warehouse
        
#         # Track if this is a new order
#         obj._is_new_order = obj.pk is None
        
#         # Track old status for stock management
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
#         """Handle order items and stock deduction"""
#         order = form.instance
        
#         # CRITICAL: Block if order is confirmed
#         if order.status in ['confirmed', 'shipped', 'delivered'] and change:
#             messages.error(
#                 request,
#                 '❌ Cannot modify items on confirmed orders. Order is locked.'
#             )
#             return  # Don't save
        
#         # Save items
#         instances = formset.save(commit=False)
        
#         for instance in instances:
#             instance.save()
        
#         # Handle deletions
#         for obj in formset.deleted_objects:
#             obj.delete()
        
#         formset.save_m2m()
        
#         # Recalculate total
#         order.calculate_total()
        
#         # Get status info
#         new_status = order.status
#         old_status = getattr(order, '_old_status', None)
#         is_new = getattr(order, '_is_new_order', False)
        
#         # Handle stock deduction/restoration based on status changes
#         if is_new and new_status in ['confirmed', 'shipped', 'delivered']:
#             # New order created as confirmed
#             if order.warehouse:
#                 try:
#                     order.deduct_stock()
#                     messages.success(
#                         request,
#                         f'✅ Order created and stock deducted from {order.warehouse.name}'
#                     )
#                 except ValidationError as e:
#                     # Stock validation failed - DELETE the order
#                     order.items.all().delete()
#                     order.delete()
#                     messages.error(request, str(e.message))
#                     return
#             else:
#                 messages.warning(request, '⚠️ No warehouse assigned - stock NOT deducted')
        
#         elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
#             # Pending to confirmed
#             if order.warehouse:
#                 try:
#                     order.deduct_stock()
#                     messages.success(
#                         request,
#                         f'✅ Order confirmed - stock deducted from {order.warehouse.name}'
#                     )
#                 except ValidationError as e:
#                     # Stock validation failed - ROLLBACK
#                     order.status = old_status
#                     order.save()
#                     messages.error(request, str(e.message))
#                     return
#             else:
#                 messages.error(request, '⚠️ No warehouse assigned')
        
#         elif change and old_status in ['confirmed', 'shipped', 'delivered'] and new_status == 'cancelled':
#             # Confirmed to cancelled - restore stock
#             if order.warehouse:
#                 order.restore_stock()
#                 messages.warning(
#                     request,
#                     f'🔄 Order cancelled - stock restored to {order.warehouse.name}'
#                 )
        
#         elif new_status == 'pending':
#             messages.info(
#                 request,
#                 'ℹ️ Order saved as Pending - stock will be deducted when confirmed'
#             )


# @admin.register(OrderItem)
# class OrderItemAdmin(OrganizationFilterMixin, admin.ModelAdmin):
#     list_display = ['order', 'product', 'quantity', 'price', 'subtotal']
#     list_filter = ['order__status', 'created_at']
#     search_fields = ['order__id', 'product__name']
    
#     def get_fields(self, request, obj=None):
#         """
#         Use different fields based on parent order status
#         Show plain text fields for confirmed orders
#         """
#         if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             return ['order_display', 'product_display', 'quantity', 'price', 'subtotal']
#         return ['order', 'product', 'quantity', 'price', 'subtotal']
    
#     def get_readonly_fields(self, request, obj=None):
#         """Make all fields readonly for confirmed order items"""
#         if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             return ['order_display', 'product_display', 'quantity', 'price', 'subtotal']
#         return ['subtotal']
    
#     def order_display(self, obj):
#         """Display order info as plain text (no link)"""
#         if obj and obj.order:
#             return format_html(
#                 '<strong>Order #{}</strong><br>'
#                 '<small style="color: #666;">Customer: {}</small><br>'
#                 '<small style="color: #666;">Status: {}</small><br>'
#                 '<small style="color: #666;">Total: €{}</small>',
#                 str(obj.order.id)[:8],
#                 obj.order.customer.name if obj.order.customer else 'N/A',
#                 obj.order.get_status_display(),
#                 obj.order.total
#             )
#         return '-'
#     order_display.short_description = 'Order'
    
#     def product_display(self, obj):
#         """Display product info as plain text (no link)"""
#         if obj and obj.product:
#             return format_html(
#                 '<strong>{}</strong><br>'
#                 '<small style="color: #666;">SKU: {}</small><br>'
#                 '<small style="color: #666;">Price: €{}</small>',
#                 obj.product.name,
#                 obj.product.sku or 'N/A',
#                 obj.product.selling_price
#             )
#         return '-'
#     product_display.short_description = 'Product'
    
#     def get_fieldsets(self, request, obj=None):
#         """Show warning for confirmed order items"""
#         if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             fieldsets = [
#                 (None, {
#                     'fields': (),
#                     'description': format_html(
#                         '<div style="background: #fff3cd; border: 2px solid #ffc107; '
#                         'padding: 15px; border-radius: 5px; margin-bottom: 20px;">'
#                         '<strong style="color: #856404; font-size: 16px;">🔒 ORDER ITEM LOCKED</strong><br>'
#                         '<span style="color: #856404;">This item belongs to a {} order and cannot be modified. '
#                         'Stock has already been deducted. '
#                         'You can only view this item. To remove it, delete the entire order (stock will be restored).</span>'
#                         '</div>',
#                         obj.order.get_status_display()
#                     )
#                 }),
#                 ('Order Item Details', {
#                     'fields': ('order_display', 'product_display', 'quantity', 'price', 'subtotal')
#                 }),
#             ]
#         else:
#             fieldsets = [
#                 ('Order Item Details', {
#                     'fields': ('order', 'product', 'quantity', 'price', 'subtotal')
#                 }),
#             ]
        
#         return fieldsets
    
#     def has_change_permission(self, request, obj=None):
#         """Prevent editing confirmed order items"""
#         if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             return False
#         return super().has_change_permission(request, obj)
    
#     def has_delete_permission(self, request, obj=None):
#         """
#         IMPORTANT: Always return True to allow CASCADE delete from parent Order
#         Block direct deletion in delete_model() and delete_queryset() instead
#         """
#         return super().has_delete_permission(request, obj)
    
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         """Override change view for confirmed order items"""
#         extra_context = extra_context or {}
        
#         try:
#             obj = self.get_object(request, object_id)
#             if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#                 extra_context['show_save'] = False
#                 extra_context['show_save_and_continue'] = False
#                 extra_context['show_save_and_add_another'] = False
#                 extra_context['show_delete'] = False
#                 extra_context['title'] = f'View Order Item (Read-Only)'
#         except:
#             pass
        
#         return super().change_view(request, object_id, form_url, extra_context)
    
#     def save_model(self, request, obj, form, change):
#         """
#         CRITICAL: Block saving confirmed order items
#         Safety net in case form bypasses permissions
#         """
#         if change and obj.pk:
#             try:
#                 old_item = OrderItem.objects.select_related('order').get(pk=obj.pk)
#                 if old_item.order.status in ['confirmed', 'shipped', 'delivered']:
#                     messages.error(
#                         request,
#                         '❌ Cannot modify items from confirmed orders. This item is locked.'
#                     )
#                     return
#             except OrderItem.DoesNotExist:
#                 pass
        
#         # Check if parent order is confirmed
#         if obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             messages.error(
#                 request,
#                 '❌ Cannot add/modify items to confirmed orders. The order is locked.'
#             )
#             return
        
#         super().save_model(request, obj, form, change)
        
#         # Recalculate order total
#         if obj.order:
#             obj.order.calculate_total()
    
#     def delete_model(self, request, obj):
#         """
#         Block DIRECT deletion of confirmed order items
#         This is called when user clicks delete button on OrderItem admin
#         CASCADE deletes from parent Order are allowed (they bypass this)
#         """
#         if obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
#             messages.error(
#                 request,
#                 '❌ Cannot delete items from confirmed orders. '
#                 'Delete the entire order instead (stock will be restored).'
#             )
#             return
        
#         # Get order before deleting item
#         order = obj.order
        
#         super().delete_model(request, obj)
        
#         # Recalculate order total
#         if order:
#             order.calculate_total()
#             messages.success(request, '✅ Order item deleted')
    
#     def delete_queryset(self, request, queryset):
#         """
#         Block DIRECT bulk deletion of confirmed order items
#         This is called when user selects items and chooses bulk delete action
#         CASCADE deletes from parent Order are allowed (they bypass this)
#         """
#         confirmed_items = queryset.filter(
#             order__status__in=['confirmed', 'shipped', 'delivered']
#         )
        
#         if confirmed_items.exists():
#             messages.error(
#                 request,
#                 f'❌ Cannot delete {confirmed_items.count()} items from confirmed orders. '
#                 'Delete entire orders instead.'
#             )
#             # Only delete items from non-confirmed orders
#             queryset = queryset.exclude(
#                 order__status__in=['confirmed', 'shipped', 'delivered']
#             )
        
#         if queryset.exists():
#             orders_to_update = set(queryset.values_list('order_id', flat=True))
#             count = queryset.count()
#             queryset.delete()
            
#             # Recalculate totals for affected orders
#             for order_id in orders_to_update:
#                 try:
#                     order = Order.objects.get(pk=order_id)
#                     order.calculate_total()
#                 except Order.DoesNotExist:
#                     pass
            
#             messages.success(request, f'✅ Deleted {count} order items')


# apps/sales/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.contrib import messages
from django import forms
from django.urls import reverse
from apps.core.admin import OrganizationFilterMixin
from .models import Customer, Order, OrderItem
from apps.inventory.models import Product

@admin.register(Customer)
class CustomerAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product_display', 'quantity', 'price', 'subtotal']
    readonly_fields = ['product_display', 'quantity', 'price', 'subtotal']
    
    def get_fields(self, request, obj=None):
        """Show different fields based on order status"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return ['product_display', 'quantity', 'price', 'subtotal']
        return ['product', 'quantity', 'price', 'subtotal']
    
    def get_readonly_fields(self, request, obj=None):
        """Make ALL fields readonly for confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return ['product_display', 'quantity', 'price', 'subtotal']
        return ['subtotal']
    
    def product_display(self, obj):
        """
        Display product as a view-only link for confirmed orders
        Links to a custom read-only product view
        """
        if obj and obj.product:
            # Create a link that goes to product detail but in read-only mode
            url = reverse('admin:inventory_product_change', args=[obj.product.id])
            return format_html(
                '<a href="{}" onclick="return confirm(\'⚠️ This product is part of a confirmed order. You can VIEW but not EDIT it.\');">'
                '{}</a>',
                url,
                obj.product.name
            )
        return '-'
    product_display.short_description = 'Product'
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding items to confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return False
        return super().has_add_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing items on confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting items on confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Order)
class OrderAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = ['id', 'customer', 'warehouse', 'total', 'status', 'created_at']
    list_filter = ['status', 'warehouse', 'created_at']
    search_fields = ['customer__name', 'id']
    inlines = [OrderItemInline]
    
    def get_fields(self, request, obj=None):
        """
        Use different fields for confirmed orders
        Display custom read-only fields without clickable links
        """
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return ['customer_display', 'warehouse_display', 'status', 'notes', 'total']
        return ['customer', 'warehouse', 'status', 'notes', 'total']
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only for confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            return ['customer_display', 'warehouse_display', 'status', 'notes', 'total']
        return ['total']
    
    def customer_display(self, obj):
        """Display customer name as plain text (no clickable link)"""
        if obj and obj.customer:
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #666;">Email: {}</small><br>'
                '<small style="color: #666;">Phone: {}</small>',
                obj.customer.name,
                obj.customer.email or 'N/A',
                obj.customer.phone or 'N/A'
            )
        return '-'
    customer_display.short_description = 'Customer'
    
    def warehouse_display(self, obj):
        """Display warehouse name as plain text (no clickable link)"""
        if obj and obj.warehouse:
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #666;">Location: {}</small>',
                obj.warehouse.name,
                obj.warehouse.location or 'N/A'
            )
        return '-'
    warehouse_display.short_description = 'Warehouse'
    
    def get_fieldsets(self, request, obj=None):
        """Show warning message for confirmed orders"""
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            # Confirmed order - use display fields
            fieldsets = [
                (None, {
                    'fields': (),
                    'description': format_html(
                        '<div style="background: #fff3cd; border: 2px solid #ffc107; '
                        'padding: 15px; border-radius: 5px; margin-bottom: 20px;">'
                        '<strong style="color: #856404; font-size: 16px;">🔒 ORDER LOCKED</strong><br>'
                        '<span style="color: #856404;">This order is {} and cannot be modified. '
                        'Stock has already been deducted. '
                        'You can only view or delete this order (stock will be restored upon deletion).</span>'
                        '</div>',
                        obj.get_status_display()
                    )
                }),
                ('Order Information', {
                    'fields': ('customer_display', 'warehouse_display', 'status', 'notes')
                }),
                ('Financial', {
                    'fields': ('total',)
                }),
            ]
        else:
            # Pending/cancelled order - use normal fields
            fieldsets = [
                ('Order Information', {
                    'fields': ('customer', 'warehouse', 'status', 'notes')
                }),
                ('Financial', {
                    'fields': ('total',)
                }),
            ]
        
        return fieldsets
    
    def has_change_permission(self, request, obj=None):
        """
        CRITICAL: Prevent editing confirmed orders entirely
        Return False to disable the save buttons
        """
        if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
            # Allow viewing but not changing
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of any order (stock will be restored)"""
        return super().has_delete_permission(request, obj)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change view to allow viewing confirmed orders"""
        extra_context = extra_context or {}
        
        try:
            obj = self.get_object(request, object_id)
            if obj and obj.status in ['confirmed', 'shipped', 'delivered']:
                extra_context['show_save'] = False
                extra_context['show_save_and_continue'] = False
                extra_context['show_save_and_add_another'] = False
                extra_context['title'] = f'View Order (Read-Only)'
        except:
            pass
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def delete_model(self, request, obj):
        """When deleting order, restore stock if it was confirmed"""
        if obj.status in ['confirmed', 'shipped', 'delivered']:
            if obj.warehouse:
                obj.restore_stock()
                messages.success(
                    request,
                    f'✅ Order deleted and stock restored to {obj.warehouse.name}'
                )
        
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Bulk delete - restore stock for all confirmed orders"""
        for obj in queryset:
            if obj.status in ['confirmed', 'shipped', 'delivered'] and obj.warehouse:
                obj.restore_stock()
        
        count = queryset.count()
        queryset.delete()
        
        messages.success(
            request,
            f'✅ Deleted {count} orders and restored stock where applicable'
        )
    
    def save_model(self, request, obj, form, change):
        """
        CRITICAL: Block any attempts to save confirmed orders
        This is a safety net in case form submission bypasses permissions
        """
        # Check if trying to modify a confirmed order
        if change and obj.pk:
            try:
                old_order = Order.objects.get(pk=obj.pk)
                if old_order.status in ['confirmed', 'shipped', 'delivered']:
                    messages.error(
                        request,
                        '❌ Cannot modify confirmed/shipped/delivered orders. This order is locked.'
                    )
                    return  # Don't save
            except Order.DoesNotExist:
                pass
        
        # Auto-assign warehouse if user has one
        if not obj.warehouse and hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            obj.warehouse = request.user.assigned_warehouse
        
        # Track if this is a new order
        obj._is_new_order = obj.pk is None
        
        # Track old status for stock management
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
        """Handle order items and stock deduction"""
        order = form.instance
        
        # CRITICAL: Block if order is confirmed
        if order.status in ['confirmed', 'shipped', 'delivered'] and change:
            messages.error(
                request,
                '❌ Cannot modify items on confirmed orders. Order is locked.'
            )
            return  # Don't save
        
        # Save items
        instances = formset.save(commit=False)
        
        for instance in instances:
            instance.save()
        
        # Handle deletions
        for obj in formset.deleted_objects:
            obj.delete()
        
        formset.save_m2m()
        
        # Recalculate total
        order.calculate_total()
        
        # Get status info
        new_status = order.status
        old_status = getattr(order, '_old_status', None)
        is_new = getattr(order, '_is_new_order', False)
        
        # Handle stock deduction/restoration based on status changes
        if is_new and new_status in ['confirmed', 'shipped', 'delivered']:
            # New order created as confirmed
            if order.warehouse:
                try:
                    order.deduct_stock()
                    messages.success(
                        request,
                        f'✅ Order created and stock deducted from {order.warehouse.name}'
                    )
                except ValidationError as e:
                    # Stock validation failed - DELETE the order
                    order.items.all().delete()
                    order.delete()
                    messages.error(request, str(e.message))
                    return
            else:
                messages.warning(request, '⚠️ No warehouse assigned - stock NOT deducted')
        
        elif change and old_status == 'pending' and new_status in ['confirmed', 'shipped', 'delivered']:
            # Pending to confirmed
            if order.warehouse:
                try:
                    order.deduct_stock()
                    messages.success(
                        request,
                        f'✅ Order confirmed - stock deducted from {order.warehouse.name}'
                    )
                except ValidationError as e:
                    # Stock validation failed - ROLLBACK
                    order.status = old_status
                    order.save()
                    messages.error(request, str(e.message))
                    return
            else:
                messages.error(request, '⚠️ No warehouse assigned')
        
        elif change and old_status in ['confirmed', 'shipped', 'delivered'] and new_status == 'cancelled':
            # Confirmed to cancelled - restore stock
            if order.warehouse:
                order.restore_stock()
                messages.warning(
                    request,
                    f'🔄 Order cancelled - stock restored to {order.warehouse.name}'
                )
        
        elif new_status == 'pending':
            messages.info(
                request,
                'ℹ️ Order saved as Pending - stock will be deducted when confirmed'
            )


@admin.register(OrderItem)
class OrderItemAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status', 'created_at']
    search_fields = ['order__id', 'product__name']
    
    def get_fields(self, request, obj=None):
        """
        Use different fields based on parent order status
        Show plain text fields for confirmed orders
        """
        if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            return ['order_display', 'product_display', 'quantity', 'price', 'subtotal']
        return ['order', 'product', 'quantity', 'price', 'subtotal']
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for confirmed order items"""
        if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            return ['order_display', 'product_display', 'quantity', 'price', 'subtotal']
        return ['subtotal']
    
    def order_display(self, obj):
        """Display order info as plain text (no link)"""
        if obj and obj.order:
            return format_html(
                '<strong>Order #{}</strong><br>'
                '<small style="color: #666;">Customer: {}</small><br>'
                '<small style="color: #666;">Status: {}</small><br>'
                '<small style="color: #666;">Total: €{}</small>',
                str(obj.order.id)[:8],
                obj.order.customer.name if obj.order.customer else 'N/A',
                obj.order.get_status_display(),
                obj.order.total
            )
        return '-'
    order_display.short_description = 'Order'
    
    def product_display(self, obj):
        """Display product info as plain text (no link)"""
        if obj and obj.product:
            return format_html(
                '<strong>{}</strong><br>'
                '<small style="color: #666;">SKU: {}</small><br>'
                '<small style="color: #666;">Price: €{}</small>',
                obj.product.name,
                obj.product.sku or 'N/A',
                obj.product.selling_price
            )
        return '-'
    product_display.short_description = 'Product'
    
    def get_fieldsets(self, request, obj=None):
        """Show warning for confirmed order items"""
        if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            fieldsets = [
                (None, {
                    'fields': (),
                    'description': format_html(
                        '<div style="background: #fff3cd; border: 2px solid #ffc107; '
                        'padding: 15px; border-radius: 5px; margin-bottom: 20px;">'
                        '<strong style="color: #856404; font-size: 16px;">🔒 ORDER ITEM LOCKED</strong><br>'
                        '<span style="color: #856404;">This item belongs to a {} order and cannot be modified. '
                        'Stock has already been deducted. '
                        'You can only view this item. To remove it, delete the entire order (stock will be restored).</span>'
                        '</div>',
                        obj.order.get_status_display()
                    )
                }),
                ('Order Item Details', {
                    'fields': ('order_display', 'product_display', 'quantity', 'price', 'subtotal')
                }),
            ]
        else:
            fieldsets = [
                ('Order Item Details', {
                    'fields': ('order', 'product', 'quantity', 'price', 'subtotal')
                }),
            ]
        
        return fieldsets
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing confirmed order items"""
        if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        IMPORTANT: Always return True to allow CASCADE delete from parent Order
        Block direct deletion in delete_model() and delete_queryset() instead
        """
        return super().has_delete_permission(request, obj)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change view for confirmed order items"""
        extra_context = extra_context or {}
        
        try:
            obj = self.get_object(request, object_id)
            if obj and obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
                extra_context['show_save'] = False
                extra_context['show_save_and_continue'] = False
                extra_context['show_save_and_add_another'] = False
                extra_context['show_delete'] = False
                extra_context['title'] = f'View Order Item (Read-Only)'
        except:
            pass
        
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """
        CRITICAL: Block saving confirmed order items
        Safety net in case form bypasses permissions
        """
        if change and obj.pk:
            try:
                old_item = OrderItem.objects.select_related('order').get(pk=obj.pk)
                if old_item.order.status in ['confirmed', 'shipped', 'delivered']:
                    messages.error(
                        request,
                        '❌ Cannot modify items from confirmed orders. This item is locked.'
                    )
                    return
            except OrderItem.DoesNotExist:
                pass
        
        # Check if parent order is confirmed
        if obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            messages.error(
                request,
                '❌ Cannot add/modify items to confirmed orders. The order is locked.'
            )
            return
        
        super().save_model(request, obj, form, change)
        
        # Recalculate order total
        if obj.order:
            obj.order.calculate_total()
    
    def delete_model(self, request, obj):
        """
        Block DIRECT deletion of confirmed order items
        This is called when user clicks delete button on OrderItem admin
        CASCADE deletes from parent Order are allowed (they bypass this)
        """
        if obj.order and obj.order.status in ['confirmed', 'shipped', 'delivered']:
            messages.error(
                request,
                '❌ Cannot delete items from confirmed orders. '
                'Delete the entire order instead (stock will be restored).'
            )
            return
        
        # Get order before deleting item
        order = obj.order
        
        super().delete_model(request, obj)
        
        # Recalculate order total
        if order:
            order.calculate_total()
            messages.success(request, '✅ Order item deleted')
    
    def delete_queryset(self, request, queryset):
        """
        Block DIRECT bulk deletion of confirmed order items
        This is called when user selects items and chooses bulk delete action
        CASCADE deletes from parent Order are allowed (they bypass this)
        """
        confirmed_items = queryset.filter(
            order__status__in=['confirmed', 'shipped', 'delivered']
        )
        
        if confirmed_items.exists():
            messages.error(
                request,
                f'❌ Cannot delete {confirmed_items.count()} items from confirmed orders. '
                'Delete entire orders instead.'
            )
            # Only delete items from non-confirmed orders
            queryset = queryset.exclude(
                order__status__in=['confirmed', 'shipped', 'delivered']
            )
        
        if queryset.exists():
            orders_to_update = set(queryset.values_list('order_id', flat=True))
            count = queryset.count()
            queryset.delete()
            
            # Recalculate totals for affected orders
            for order_id in orders_to_update:
                try:
                    order = Order.objects.get(pk=order_id)
                    order.calculate_total()
                except Order.DoesNotExist:
                    pass
            
            messages.success(request, f'✅ Deleted {count} order items')
