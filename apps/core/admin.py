from django.contrib import admin


class OrganizationFilterMixin:
    """
    Mixin to automatically filter querysets by organization.
    Handles both direct organization fields and warehouse-based filtering.
    """
    
    def get_queryset(self, request):
        """Filter queryset based on user's organization and warehouse"""
        qs = super().get_queryset(request)
        
        # Superuser sees everything
        if request.user.is_superuser:
            return qs
        
        # Users without organization see nothing
        if not hasattr(request.user, 'organization') or not request.user.organization:
            return qs.none()
        
        user_org = request.user.organization
        user_warehouse = getattr(request.user, 'assigned_warehouse', None)
        model = qs.model
        model_name = model.__name__
        
        # Strategy 1: Model has organization field directly (Warehouse, Organization)
        if hasattr(model, 'organization'):
            return qs.filter(organization=user_org)
        
        # Strategy 2: Model has warehouse field (Order, Stock)
        if hasattr(model, 'warehouse'):
            if user_warehouse:
                return qs.filter(warehouse=user_warehouse)
            return qs.filter(warehouse__organization=user_org)
        
        # Strategy 3: OrderItem - filter by order's warehouse
        if model_name == 'OrderItem':
            if user_warehouse:
                return qs.filter(order__warehouse=user_warehouse)
            return qs.filter(order__warehouse__organization=user_org)
        
        # Strategy 4: Customer - filter by orders' warehouse organization
        # Customers are shown if they have orders in user's organization
        if model_name == 'Customer':
            if user_warehouse:
                # Show customers who have orders at this warehouse
                return qs.filter(orders__warehouse=user_warehouse).distinct()
            # Show customers who have orders at any warehouse in organization
            return qs.filter(orders__warehouse__organization=user_org).distinct()
        
        # Strategy 5: Model has created_by field (Product)
        if hasattr(model, 'created_by'):
            return qs.filter(created_by__organization=user_org)
        
        # Fallback: show all (for shared resources like customers)
        return qs
        # Fallback: show nothing
        return qs.none()
    def save_model(self, request, obj, form, change):
        """Auto-assign organization and audit fields"""
        if not change:  # Creating new object
            # Set created_by
            if hasattr(obj, 'created_by') and not obj.created_by:
                obj.created_by = request.user
            
            # Set organization if model has it
            if hasattr(obj, 'organization') and not obj.organization:
                if hasattr(request.user, 'organization') and request.user.organization:
                    obj.organization = request.user.organization
            
            # Set warehouse if user has assigned warehouse and model supports it
            if hasattr(obj, 'warehouse') and not obj.warehouse:
                if hasattr(request.user, 'assigned_warehouse') and request.user.assigned_warehouse:
                    obj.warehouse = request.user.assigned_warehouse
        else:  # Updating object
            if hasattr(obj, 'updated_by'):
                obj.updated_by = request.user
        
        super().save_model(request, obj, form, change)


def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """
    Filter foreign key choices by organization and warehouse.
    CRITICAL: Enforce strict multi-tenancy - users only see their organization's data
    """
    # Superuser sees everything
    if request.user.is_superuser:
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # For all other users, apply organization filtering
    user_org = getattr(request.user, 'organization', None)
    user_warehouse = getattr(request.user, 'assigned_warehouse', None)
    
    if not user_org:
        # User has no organization - show nothing
        if db_field.name == "warehouse":
            from apps.inventory.models import Warehouse
            kwargs["queryset"] = Warehouse.objects.none()
        elif db_field.name == "customer":
            from apps.sales.models import Customer
            kwargs["queryset"] = Customer.objects.none()
        elif db_field.name == "product":
            from apps.inventory.models import Product
            kwargs["queryset"] = Product.objects.none()
        elif db_field.name == "organization":
            from apps.accounts.models import Organization
            kwargs["queryset"] = Organization.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Apply organization-based filtering
    
    # 1. WAREHOUSES - Show only user's organization warehouses
    if db_field.name == "warehouse":
        from apps.inventory.models import Warehouse
        if user_warehouse:
            # Staff with assigned warehouse - show ONLY their warehouse
            kwargs["queryset"] = Warehouse.objects.filter(id=user_warehouse.id)
        else:
            # Admin/Manager - show all warehouses in THEIR organization
            kwargs["queryset"] = Warehouse.objects.filter(organization=user_org)
    
    # 2. PRODUCTS - Show only user's organization products
    elif db_field.name == "product":
        from apps.inventory.models import Product
        kwargs["queryset"] = Product.objects.filter(created_by__organization=user_org)
    
    # 3. CUSTOMERS - Show only user's organization customers
    elif db_field.name == "customer":
        from apps.sales.models import Customer
        kwargs["queryset"] = Customer.objects.filter(organization=user_org)
    
    # 4. ORGANIZATION - Non-superusers should NEVER see organization dropdown
    #    Auto-assign their own organization instead
    elif db_field.name == "organization":
        from apps.accounts.models import Organization
        # Show ONLY their organization (or none if switching would break data)
        kwargs["queryset"] = Organization.objects.filter(id=user_org.id)
    
    return super().formfield_for_foreignkey(db_field, request, **kwargs)
