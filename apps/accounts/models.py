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
#apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel
from django.utils import timezone

class Organization(BaseModel):
    """Organization/Company - each client is one organization"""
    name = models.CharField(max_length=255, help_text="Client company name")
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")
    is_active = models.BooleanField(default=True)
    
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial'
    )
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    trial_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def warehouse_count(self):
        return self.warehouses.count()
    
    @property
    def user_count(self):
        return self.users.count()


class User(AbstractUser, BaseModel):
    """Custom user model"""
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
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )
    
    assigned_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_users'
    )

    date_joined = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = "users"
    
    def __str__(self):
        return self.username
