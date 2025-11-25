from django.db import models
from apps.core.models import TrackableModel


class Warehouse(TrackableModel):
    """Warehouse/storage location"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "warehouses"
        
    def __str__(self):
        return self.name


class Product(TrackableModel):
    """Product master data"""
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"
        
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
        
    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"
