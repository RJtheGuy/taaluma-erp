from django.db import models
from apps.core.models import TrackableModel


class Customer(TrackableModel):
    """Customer master data"""
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "customers"
        
    def __str__(self):
        return self.name


class Order(TrackableModel):
    """Sales order"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="orders")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Order #{self.id} - {self.customer}"


class OrderItem(TrackableModel):
    """Order line items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "order_items"
        
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
