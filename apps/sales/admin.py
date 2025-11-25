from django.contrib import admin
from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # KEEP EXACTLY AS IS
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    # KEEP EXACTLY AS IS
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # KEEP YOUR EXACT FIELDS - don't change them!
    list_display = ['id', 'customer', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name']
    inlines = [OrderItemInline]
    
    # ADD THIS METHOD ONLY IF Order model has 'warehouse' field:
    # (Check your sales/models.py - does Order have warehouse field?)
    # If YES, uncomment this:
    
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     
    #     if request.user.is_superuser:
    #         return qs
    #     
    #     if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
    #         return qs.filter(warehouse=request.user.assigned_warehouse)
    #     
    #     return qs
