# accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # UUID Primary Key - REQUIRED!
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    
    assigned_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_users',
        help_text="Warehouse/location this user is assigned to",
        verbose_name="Assigned Location"
    )
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def get_accessible_warehouses(self):
        from inventory.models import Warehouse
        
        if self.is_superuser:
            return Warehouse.objects.all()
        
        if self.groups.filter(name="OWNER (Client Admin)").exists():
            return Warehouse.objects.all()
        
        if self.groups.filter(name="GENERAL MANAGER (Multi-location oversight)").exists():
            return Warehouse.objects.all()
        
        if self.groups.filter(name="INVENTORY MANAGER (All locations)").exists():
            return Warehouse.objects.all()
        
        if self.groups.filter(name__in=[
            "STORE MANAGER (Location-specific)",
            "STORE STAFF (Order entry)"
        ]).exists():
            if self.assigned_warehouse:
                return Warehouse.objects.filter(id=self.assigned_warehouse.id)
            else:
                return Warehouse.objects.none()
        
        return Warehouse.objects.none()
    
    def can_access_warehouse(self, warehouse):
        return warehouse in self.get_accessible_warehouses()
