# apps/core/admin.py
from django.contrib import admin


class OrganizationFilterMixin:
    """
    Mixin to automatically filter querysets by organization.
    Add this to any ModelAdmin that needs multi-tenancy.
    
    Usage:
        class MyAdmin(OrganizationFilterMixin, admin.ModelAdmin):
            ...
    """
    
    def get_queryset(self, request):
        """Filter queryset based on user's organization"""
        qs = super().get_queryset(request)
        
        # Superuser sees everything
        if request.user.is_superuser:
            return qs
        
        # Users without organization see nothing
        if not hasattr(request.user, 'organization') or not request.user.organization:
            return qs.none()
        
        user_org = request.user.organization
        model = qs.model
        
        # Strategy 1: Model has organization field directly (Warehouse)
        if hasattr(model, 'organization'):
            return qs.filter(organization=user_org)
        
        # Strategy 2: Model has warehouse field (Order, Stock)
        if hasattr(model, 'warehouse'):
            return qs.filter(warehouse__organization=user_org)
        
        # Strategy 3: Model has created_by field (Product, Customer)
        if hasattr(model, 'created_by'):
            return qs.filter(created_by__organization=user_org)
        
        # Fallback: show nothing
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """Auto-assign organization on create"""
        if not change:  # Creating new object
            # If model has organization field and it's not set
            if hasattr(obj, 'organization') and not obj.organization:
                if hasattr(request.user, 'organization') and request.user.organization:
                    obj.organization = request.user.organization
        
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter foreign key choices by organization.
        For example, when creating an Order, only show warehouses from user's org.
        """
        if not request.user.is_superuser:
            user_org = getattr(request.user, 'organization', None)
            
            if user_org:
                # Filter warehouses
                if db_field.name == "warehouse":
                    from apps.inventory.models import Warehouse
                    kwargs["queryset"] = Warehouse.objects.filter(organization=user_org)
                
                # Filter products (by creator's organization)
                if db_field.name == "product":
                    from apps.inventory.models import Product
                    kwargs["queryset"] = Product.objects.filter(created_by__organization=user_org)
                
                # Filter customers (by creator's organization)
                if db_field.name == "customer":
                    from apps.sales.models import Customer
                    kwargs["queryset"] = Customer.objects.filter(created_by__organization=user_org)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
