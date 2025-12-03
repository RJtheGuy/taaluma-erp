# from django.db import models
# from apps.core.models import TrackableModel


# class Warehouse(TrackableModel):
#     """Warehouse/storage location"""
#     name = models.CharField(max_length=255)
#     location = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     # ORGANIZATION - Links warehouse to client
#     organization = models.ForeignKey(
#         'accounts.Organization',
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name='warehouses',
#         help_text="Organization that owns this warehouse"
#     )
    
#     class Meta:
#         db_table = "warehouses"
#         ordering = ['name']
    
#     def __str__(self):
#         if self.organization:
#             return f"{self.name} ({self.organization.name})"
#         return self.name


# class Product(TrackableModel):
#     """Product master data"""
#     name = models.CharField(max_length=255)
#     sku = models.CharField(max_length=100, unique=True)
#     category = models.CharField(max_length=100)
#     cost_price = models.DecimalField(max_digits=10, decimal_places=2)
#     selling_price = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField(null=True, blank=True)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         db_table = "products"
        
#     def __str__(self):
#         return f"{self.name} ({self.sku})"


# class Stock(TrackableModel):
#     """Stock levels per warehouse"""
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
#     warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
#     quantity = models.IntegerField(default=0)
#     reorder_level = models.IntegerField(default=10)

#     class Meta:
#         db_table = "stocks"
#         unique_together = ["product", "warehouse"]
        
#     def __str__(self):
#         return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"


#     @property
#     def stock_status(self):
#         """Return stock status for display"""
#         if self.quantity <= 0:
#             return "out_of_stock"
#         elif self.quantity <= self.reorder_level:
#             return "low_stock"
#         else:
#             return "in_stock"


# apps/inventory/models.py

class Warehouse(TrackableModel):
    """Warehouse/storage location"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='warehouses',
        help_text="Organization that owns this warehouse"
    )
    
    class Meta:
        db_table = "warehouses"
        ordering = ['name']
        # ADD THIS ↓
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['name']),
        ]


class Product(TrackableModel):
    """Product master data"""
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # ADD THIS METHOD ↓
    def clean(self):
        """Validate product data"""
        from django.core.exceptions import ValidationError
        
        if self.cost_price < 0:
            raise ValidationError({'cost_price': 'Cost price cannot be negative'})
        
        if self.selling_price < 0:
            raise ValidationError({'selling_price': 'Selling price cannot be negative'})
        
        if self.selling_price < self.cost_price:
            raise ValidationError({
                'selling_price': 'Selling price should not be less than cost price'
            })
        
        if not self.sku or len(self.sku.strip()) < 2:
            raise ValidationError({'sku': 'SKU must be at least 2 characters'})
    
    class Meta:
        db_table = "products"
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['created_by']),
        ]
        
    def __str__(self):
        return f"{self.name} ({self.sku})"


class Stock(TrackableModel):
    """Stock levels per warehouse"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    
    class Meta:
        db_table = "stocks"
        unique_together = ["product", "warehouse"]
        # ADD THIS ↓
        indexes = [
            models.Index(fields=['warehouse', 'product']),
            models.Index(fields=['quantity']),
        ]
        
    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"
    
    @property
    def stock_status(self):
        """Return stock status for display"""
        if self.quantity <= 0:
            return "out_of_stock"
        elif self.quantity <= self.reorder_level:
            return "low_stock"
        else:
            return "in_stock"



