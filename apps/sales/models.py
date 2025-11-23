from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
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
    _stock_deducted = False  # Track if stock was already deducted

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Order #{self.id} - {self.customer}"
    
    def calculate_total(self):
        """Calculate and update order total"""
        if self.items.exists():
            self.total = sum(item.subtotal for item in self.items.all())
            Order.objects.filter(pk=self.pk).update(total=self.total)
    
    def deduct_stock(self):
        """Deduct stock quantities for all order items"""
        from apps.inventory.models import Stock
        
        if self._stock_deducted:
            return  # Already deducted, don't do it again
            
        for item in self.items.all():
            # Find stock for this product (first available warehouse)
            try:
                stock = Stock.objects.filter(
                    product=item.product,
                    quantity__gte=item.quantity  # Only if enough stock
                ).first()
                
                if stock:
                    stock.quantity -= item.quantity
                    stock.save()
                    print(f"✓ Deducted {item.quantity} units of {item.product.name} from {stock.warehouse.name}")
                else:
                    print(f"⚠ Warning: Insufficient stock for {item.product.name}")
            except Stock.DoesNotExist:
                print(f"⚠ Warning: No stock record for {item.product.name}")
        
        self._stock_deducted = True
    
    def restore_stock(self):
        """Restore stock when order is cancelled"""
        from apps.inventory.models import Stock
        
        for item in self.items.all():
            try:
                stock = Stock.objects.filter(product=item.product).first()
                if stock:
                    stock.quantity += item.quantity
                    stock.save()
                    print(f"✓ Restored {item.quantity} units of {item.product.name} to {stock.warehouse.name}")
            except Stock.DoesNotExist:
                pass


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


# Signal to handle order status changes
@receiver(pre_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """Restore stock when order is cancelled"""
    if instance.pk:  # Only for existing orders
        try:
            old_order = Order.objects.get(pk=instance.pk)
            # If status changed to cancelled, restore stock
            if old_order.status != 'cancelled' and instance.status == 'cancelled':
                instance.restore_stock()
        except Order.DoesNotExist:
            pass
