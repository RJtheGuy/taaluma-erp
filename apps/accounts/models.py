# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from apps.core.models import BaseModel


# class User(AbstractUser, BaseModel):
#     """Custom user model with phone and role"""
#     phone = models.CharField(max_length=20, null=True, blank=True)
#     role = models.CharField(max_length=50, default="staff")
    
#     # ADD THIS ONE LINE:
#     assigned_warehouse = models.ForeignKey(
#         'inventory.Warehouse',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         help_text="Warehouse this user manages"
#     )

#     class Meta:
#         app_label = 'accounts'
#         db_table = "users"
#         verbose_name = "User"
#         verbose_name_plural = "Users"

#     def __str__(self):
#         return self.username


# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel


class Organization(BaseModel):
    """Organization/Company - each client is one organization"""
    name = models.CharField(max_length=255, help_text="Client company name")
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")
    is_active = models.BooleanField(default=True)
    
    # Contact Information
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # Subscription & Billing
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial',
        help_text="Subscription status"
    )
    monthly_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=300.00,
        help_text="Monthly subscription fee in EUR"
    )
    trial_end_date = models.DateField(null=True, blank=True, help_text="Trial period end date")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes about this client")
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name
    
    @property
    def warehouse_count(self):
        """Count warehouses for this organization"""
        return self.warehouses.count()
    
    @property
    def user_count(self):
        """Count users for this organization"""
        return self.users.count()


class User(AbstractUser, BaseModel):
    """Custom user model with phone, role, and organization"""
    phone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=50, 
        default="staff",
        choices=[
            ('admin', 'Administrator'),
            ('manager', 'Manager'),
            ('staff', 'Staff'),
        ]
    )
    
    # ORGANIZATION - Multi-tenancy key field
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        help_text="Organization this user belongs to"
    )
    
    # Warehouse assignment
    assigned_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_users',
        help_text="Warehouse this user manages (optional)"
    )
    
    class Meta:
        app_label = 'accounts'
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.username} ({self.organization.name if self.organization else 'No Org'})"
    
    def save(self, *args, **kwargs):
        # If user has assigned_warehouse, inherit organization from warehouse
        if self.assigned_warehouse and self.assigned_warehouse.organization:
            self.organization = self.assigned_warehouse.organization
        super().save(*args, **kwargs)



