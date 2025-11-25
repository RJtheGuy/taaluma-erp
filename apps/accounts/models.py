from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel


class User(AbstractUser, BaseModel):
    """Custom user model with phone and role"""
    phone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=50, default="staff")
    
    # ADD THIS ONE LINE:
    assigned_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Warehouse this user manages"
    )

    class Meta:
        app_label = 'accounts'
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username
