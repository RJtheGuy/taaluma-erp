from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        return obj.created_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all, but write only to admin/manager roles
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Only managers and admins can access
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or 
            request.user.role in ['manager', 'admin']
        )


class CanManageInventory(permissions.BasePermission):
    """
    Permission for inventory management
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.role in ['manager', 'admin', 'inventory_manager']


class CanManageSales(permissions.BasePermission):
    """
    Permission for sales operations
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.role in ['manager', 'admin', 'sales_manager', 'staff']


class CanViewAnalytics(permissions.BasePermission):
    """
    Permission for viewing analytics
    """
    def has_permission(self, request, view):
        return request.user and request.user.role in ['manager', 'admin']


class IsOrganizationMember(permissions.BasePermission):
    """
    Only allow users to access their organization's data
    """
    
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Superusers see everything
        if request.user.is_superuser:
            return True
        
        user_org = getattr(request.user, 'organization', None)
        if not user_org:
            return False
        
        # Check organization match based on object type
        if hasattr(obj, 'organization'):
            return obj.organization == user_org
        
        if hasattr(obj, 'warehouse'):
            return obj.warehouse.organization == user_org
        
        if hasattr(obj, 'created_by'):
            return obj.created_by.organization == user_org
        
        return False
