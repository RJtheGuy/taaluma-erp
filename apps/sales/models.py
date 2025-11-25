# sales/models.py
from django.db import models
from apps.core.models import BaseModel
from apps.inventory.models import Product, Warehouse, Stock


class Customer(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'customers'  # Match your migration!
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Order(BaseModel):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        help_text="Warehouse fulfilling this order"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'  # Match your migration!
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{str(self.id)[:8]} - {self.customer.name if self.customer else 'No Customer'}"
    
    def calculate_total(self):
        """Calculate order total from items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save()
        return total
    
    def deduct_stock(self):
        """Deduct stock from warehouse when order is confirmed"""
        if not self.warehouse:
            return False
        
        for item in self.items.all():
            try:
                stock = Stock.objects.get(
                    product=item.product,
                    warehouse=self.warehouse
                )
                stock.quantity -= item.quantity
                stock.save()
            except Stock.DoesNotExist:
                pass
        
        return True
    
    def restore_stock(self):
        """Restore stock to warehouse when order is cancelled"""
        if not self.warehouse:
            return False
        
        for item in self.items.all():
            try:
                stock = Stock.objects.get(
                    product=item.product,
                    warehouse=self.warehouse
                )
                stock.quantity += item.quantity
                stock.save()
            except Stock.DoesNotExist:
                pass
        
        return True


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_items'  # Match your migration!
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate subtotal before saving"""
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
