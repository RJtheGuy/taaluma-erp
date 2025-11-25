# accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with warehouse assignment for location-based access control"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    assigned_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_users',
        help_text="Assign user to specific warehouse for location-based access. Leave empty for full access.",
        verbose_name="Assigned Warehouse"
    )
    
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Contact phone number"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="User can login when active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_warehouse_access(self, warehouse):
        """Check if user can access a specific warehouse"""
        # Superusers have access to everything
        if self.is_superuser:
            return True
        
        # Users without assignment have full access (owners/general managers)
        if not self.assigned_warehouse:
            return True
        
        # Users with assignment can only access their warehouse
        return self.assigned_warehouse == warehouse
