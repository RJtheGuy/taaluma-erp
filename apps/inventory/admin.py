# # apps/inventory/admin.py - UPDATE YOUR EXISTING FILE

# from django.contrib import admin
# from django.urls import path
# from django.shortcuts import redirect
# from django.utils.html import format_html
# from .models import Warehouse, Product, Stock


# @admin.register(Warehouse)
# class WarehouseAdmin(admin.ModelAdmin):
#     list_display = ['name', 'location', 'is_active', 'created_at']
#     list_filter = ['is_active', 'created_at']
#     search_fields = ['name', 'location']
#     readonly_fields = ['created_at', 'updated_at']
    
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
        
#         if request.user.is_superuser:
#             return qs
        
#         if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
#             return qs.filter(id=request.user.assigned_warehouse.id)
        
#         return qs


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'is_active']
#     list_filter = ['category', 'is_active']
#     search_fields = ['name', 'sku']
    
#     # ADD BULK UPLOAD BUTTON
#     change_list_template = 'admin/inventory/product_changelist.html'
    
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='inventory_product_bulk_upload'),
#         ]
#         return custom_urls + urls
    
#     def bulk_upload_view(self, request):
#         from apps.inventory.views import bulk_upload_products
#         return bulk_upload_products(request)


# @admin.register(Stock)
# class StockAdmin(admin.ModelAdmin):
#     list_display = ['product', 'warehouse', 'quantity_with_alert', 'reorder_level', 'updated_at']
#     list_filter = ['warehouse', 'updated_at']
#     search_fields = ['product__name', 'product__sku', 'warehouse__name']
#     readonly_fields = ['created_at', 'updated_at']
    
#     # ADD BULK UPLOAD BUTTON
#     change_list_template = 'admin/inventory/stock_changelist.html'
    
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='inventory_stock_bulk_upload'),
#         ]
#         return custom_urls + urls
    
#     def bulk_upload_view(self, request):
#         from apps.inventory.views import bulk_upload_stock
#         return bulk_upload_stock(request)
    
#     # LOW STOCK ALERT DISPLAY
#     def quantity_with_alert(self, obj):
#         """Display quantity with color-coded alert"""
#         if obj.quantity <= 0:
#             # Out of stock - RED
#             return format_html(
#                 '<span style="background: #f44336; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">🚨 {} (OUT OF STOCK)</span>',
#                 obj.quantity
#             )
#         elif obj.quantity <= obj.reorder_level:
#             # Low stock - ORANGE
#             return format_html(
#                 '<span style="background: #ff9800; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">⚠️ {} (LOW STOCK)</span>',
#                 obj.quantity
#             )
#         elif obj.quantity <= obj.reorder_level * 2:
#             # Getting low - YELLOW
#             return format_html(
#                 '<span style="background: #ffc107; color: #333; padding: 4px 12px; border-radius: 12px; font-weight: bold;">⚡ {} (REORDER SOON)</span>',
#                 obj.quantity
#             )
#         else:
#             # Good stock - GREEN
#             return format_html(
#                 '<span style="background: #4caf50; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">✅ {}</span>',
#                 obj.quantity
#             )
    
#     quantity_with_alert.short_description = 'Stock Level'
#     quantity_with_alert.admin_order_field = 'quantity'
    
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
#                 kwargs["queryset"] = Warehouse.objects.filter(id=request.user.assigned_warehouse.id)
        
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
# apps/inventory/admin.py
from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from apps.core.admin import OrganizationFilterMixin
from .models import Warehouse, Product, Stock


# @admin.register(Warehouse)
# class WarehouseAdmin(OrganizationFilterMixin, admin.ModelAdmin):
#     list_display = ['name', 'location', 'organization', 'is_active', 'stock_count', 'created_at']
#     list_filter = ['is_active', 'organization', 'created_at']
#     search_fields = ['name', 'location']
    
#     fieldsets = (
#         ('Warehouse Information', {
#             'fields': ('name', 'location', 'organization', 'is_active')
#         }),
#         ('System Info', {
#             'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

@admin.register(Warehouse)
class WarehouseAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = ['name', 'location', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_fields(self, request, obj=None):
        """Hide organization field for non-superusers"""
        fields = ['name', 'location', 'is_active']
        
        # Only superusers can see/change organization
        if request.user.is_superuser:
            fields.insert(2, 'organization')  # Add after location
        
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """Make organization readonly for non-superusers if somehow visible"""
        readonly = ['created_at', 'updated_at', 'created_by', 'updated_by']
        
        if not request.user.is_superuser:
            readonly.append('organization')
        
        return readonly
    
    fieldsets = None  # Use get_fields instead
    
    def stock_count(self, obj):
        """Display number of stock records"""
        count = obj.stocks.count()
        return format_html('<strong>{}</strong> products', count)
    stock_count.short_description = 'Stock Items'


@admin.register(Product)
class ProductAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = [
        'name', 
        'sku', 
        'category', 
        'cost_price', 
        'selling_price',
        # 'profit_margin',
        'is_active'
    ]
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'sku', 'category']
    
    # BULK UPLOAD TEMPLATE
    change_list_template = 'admin/inventory/product_changelist.html'
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'sku', 'category', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at'] 

    def get_readonly_fields(self, request, obj=None):
        """Dynamically determine readonly fields"""
        readonly = ['created_at', 'updated_at']
        
        # Only add these if model actually has them
        if hasattr(self.model, 'created_by'):
            readonly.append('created_by')
        if hasattr(self.model, 'updated_by'):
            readonly.append('updated_by')
        
        return readonly
    
    def get_fieldsets(self, request, obj=None):
        """Dynamically build fieldsets"""
        fieldsets = [
            ('Product Information', {
                'fields': ('name', 'sku', 'category', 'description', 'is_active')
            }),
            ('Pricing', {
                'fields': ('cost_price', 'selling_price')
            }),
        ]
        
        # Only add System Info if fields exist
        system_fields = []
        for field in ['created_by', 'created_at', 'updated_by', 'updated_at']:
            if hasattr(self.model, field):
                system_fields.append(field)
        
        if system_fields:
            fieldsets.append(
                ('System Info', {
                    'fields': tuple(system_fields),
                    'classes': ('collapse',)
                })
            )
        
        return fieldsets

    def get_queryset(self, request):
        """
        Products are organization-wide, not warehouse-specific
        """
        qs = super().get_queryset(request)
        
        # Superuser sees all
        if request.user.is_superuser:
            return qs
        
        # All users in organization see all organization products
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(created_by__organization=request.user.organization)
        
        return qs.none()
    
    def get_urls(self):
        """Add bulk upload URL"""
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='inventory_product_bulk_upload'),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        """Handle bulk upload"""
        from apps.inventory.views import bulk_upload_products
        return bulk_upload_products(request)
    
    # def profit_margin(self, obj):
    #     """Calculate and display profit margin"""
    #     if obj.cost_price > 0:
    #         margin = ((obj.selling_price - obj.cost_price) / obj.cost_price) * 100
    #         color = '#4caf50' if margin > 30 else '#ff9800' if margin > 10 else '#f44336'
    #         return format_html(
    #             '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
    #             color,
    #             margin
    #         )
    #     return '-'
    # profit_margin.short_description = 'Margin'

class StockLevelFilter(admin.SimpleListFilter):
    title = 'Stock Level'
    parameter_name = 'stock_level'
    
    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Stock'),
            ('out', 'Out of Stock'),
            ('ok', 'In Stock'),
        )
    
    def queryset(self, request, queryset):
        from django.db.models import F
        if self.value() == 'low':
            return queryset.filter(quantity__lte=F('reorder_level'))
        if self.value() == 'out':
            return queryset.filter(quantity=0)
        if self.value() == 'ok':
            return queryset.filter(quantity__gt=F('reorder_level'))
        return queryset

@admin.register(Stock)
class StockAdmin(OrganizationFilterMixin, admin.ModelAdmin):
    list_display = [
        'product_name', 
        'warehouse_name', 
        'quantity_display', 
        'reorder_level',
        'stock_status_badge',
        'last_updated'
    ]
    list_filter = ['warehouse', 'product__category', StockLevelFilter]
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    readonly_fields = ['stock_status_badge', 'last_updated']
    
    # IMPORTANT: Allow filtering by warehouse
    autocomplete_fields = ['product']
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('product', 'warehouse', 'quantity', 'reorder_level')
        }),
        ('Status', {
            'fields': ('stock_status_badge', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Override to ensure warehouse staff see their warehouse's stock
        """
        qs = super().get_queryset(request)
        
        # Superuser sees all
        if request.user.is_superuser:
            return qs
        
        # User with assigned warehouse - see only that warehouse's stock
        if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
            return qs.filter(warehouse=request.user.assigned_warehouse)
        
        # User with organization but no warehouse - see all org's stock
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(warehouse__organization=request.user.organization)
        
        return qs.none()
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'
    
    def warehouse_name(self, obj):
        return obj.warehouse.name
    warehouse_name.short_description = 'Warehouse'
    warehouse_name.admin_order_field = 'warehouse__name'
    
    def quantity_display(self, obj):
        if obj.quantity <= 0:
            color = '#d32f2f'  # Red
            icon = '🔴'
        elif obj.quantity <= obj.reorder_level:
            color = '#f57c00'  # Orange
            icon = '🟠'
        elif obj.quantity <= obj.reorder_level * 2:
            color = '#fbc02d'  # Yellow
            icon = '🟡'
        else:
            color = '#388e3c'  # Green
            icon = '🟢'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.quantity
        )
    quantity_display.short_description = 'Quantity'
    quantity_display.admin_order_field = 'quantity'
    
    def stock_status_badge(self, obj):
        status = obj.stock_status
        colors = {
            'in_stock': '#4caf50',
            'low_stock': '#ff9800',
            'out_of_stock': '#f44336'
        }
        labels = {
            'in_stock': 'IN STOCK',
            'low_stock': 'LOW STOCK',
            'out_of_stock': 'OUT OF STOCK'
        }
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold; display: inline-block;">{}</span>',
            colors.get(status, '#9e9e9e'),
            labels.get(status, 'UNKNOWN')
        )
    stock_status_badge.short_description = 'Status'
    
    def last_updated(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    last_updated.short_description = 'Last Updated'
    
    # Custom actions
    actions = ['bulk_increase_stock', 'bulk_decrease_stock', 'mark_for_reorder']
    
    def bulk_increase_stock(self, request, queryset):
        """Increase stock by 10 units"""
        updated = queryset.update(quantity=F('quantity') + 10)
        self.message_user(request, f'{updated} stock records increased by 10 units.')
    bulk_increase_stock.short_description = 'Increase stock by 10 units'
    
    def bulk_decrease_stock(self, request, queryset):
        """Decrease stock by 10 units"""
        updated = queryset.filter(quantity__gte=10).update(quantity=F('quantity') - 10)
        self.message_user(request, f'{updated} stock records decreased by 10 units.')
    bulk_decrease_stock.short_description = 'Decrease stock by 10 units'
    
    def mark_for_reorder(self, request, queryset):
        """Mark items as needing reorder"""
        count = queryset.count()
        self.message_user(request, f'{count} items marked for reorder.')
    mark_for_reorder.short_description = 'Mark for reorder'

# @admin.register(Stock)
# class StockAdmin(OrganizationFilterMixin, admin.ModelAdmin):
#     list_display = [
#         'product', 
#         'warehouse', 
#         'quantity_display',
#         'reorder_level',
#         'stock_status_display',
#         'updated_at'
#     ]
#     list_filter = ['warehouse', 'created_at']
#     search_fields = ['product__name', 'product__sku', 'warehouse__name']
    
#     # BULK UPLOAD TEMPLATE
#     change_list_template = 'admin/inventory/stock_changelist.html'
    
#     fieldsets = (
#         ('Stock Information', {
#             'fields': ('product', 'warehouse', 'quantity', 'reorder_level')
#         }),
#         ('System Info', {
#             'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']
    
#     def get_urls(self):
#         """Add bulk upload URL"""
#         urls = super().get_urls()
#         custom_urls = [
#             path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='inventory_stock_bulk_upload'),
#         ]
#         return custom_urls + urls
    
#     def bulk_upload_view(self, request):
#         """Handle bulk upload"""
#         from apps.inventory.views import bulk_upload_stock
#         return bulk_upload_stock(request)
    
#     def quantity_display(self, obj):
#         """Display quantity with color coding"""
#         if obj.quantity <= 0:
#             color = '#f44336'
#             icon = '❌'
#         elif obj.quantity <= obj.reorder_level:
#             color = '#ff9800'
#             icon = '⚠️'
#         else:
#             color = '#4caf50'
#             icon = '✅'
        
#         return format_html(
#             '<span style="color: {}; font-weight: bold;">{} {}</span>',
#             color,
#             icon,
#             obj.quantity
#         )
#     quantity_display.short_description = 'Quantity'
#     quantity_display.admin_order_field = 'quantity'
    
#     def stock_status_display(self, obj):
#         """Display stock status badge"""
#         status = obj.stock_status
        
#         badges = {
#             'out_of_stock': ('OUT OF STOCK', '#f44336'),
#             'low_stock': ('LOW STOCK', '#ff9800'),
#             'in_stock': ('IN STOCK', '#4caf50'),
#         }
        
#         text, color = badges.get(status, ('UNKNOWN', '#9e9e9e'))
        
#         return format_html(
#             '<span style="background: {}; color: white; padding: 4px 12px; '
#             'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
#             color,
#             text
#         )
#     stock_status_display.short_description = 'Status'
