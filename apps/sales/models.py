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
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="orders"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name if self.customer else 'No Customer'}"
    
    def calculate_total(self):
        """Calculate and update order total from all items"""
        if not self.pk:
            return  # Can't calculate if order not saved yet
            
        total = sum(item.subtotal for item in self.items.all())
        
        # Update without triggering signals
        Order.objects.filter(pk=self.pk).update(total=total)
        self.total = total  # Update instance too
        
        return total
    
    def deduct_stock(self):
        """
        Deduct stock quantities for all order items.
        Deducts from first available warehouse with sufficient stock.
        """
        from apps.inventory.models import Stock
        
        if not self.items.exists():
            print(f"⚠️ Warning: Order #{self.id} has no items to deduct stock from")
            return
        
        deduction_log = []
        
        for item in self.items.all():
            # Find stock with sufficient quantity
            stock = Stock.objects.filter(
                product=item.product,
                quantity__gte=item.quantity
            ).first()
            
            if stock:
                old_qty = stock.quantity
                stock.quantity -= item.quantity
                stock.save()
                
                deduction_log.append(
                    f"✓ {item.product.name}: {old_qty} → {stock.quantity} "
                    f"(deducted {item.quantity} from {stock.warehouse.name})"
                )
            else:
                # Check if product exists but insufficient stock
                any_stock = Stock.objects.filter(product=item.product).first()
                if any_stock:
                    deduction_log.append(
                        f"⚠️ {item.product.name}: Insufficient stock "
                        f"(need {item.quantity}, available {any_stock.quantity})"
                    )
                else:
                    deduction_log.append(
                        f"❌ {item.product.name}: No stock record found"
                    )
        
        # Print deduction log
        print(f"\n{'='*60}")
        print(f"Stock Deduction for Order #{self.id}")
        print(f"{'='*60}")
        for log in deduction_log:
            print(log)
        print(f"{'='*60}\n")
        
        return deduction_log
    
    def restore_stock(self):
        """
        Restore stock when order is cancelled.
        Adds back to the first stock record found for each product.
        """
        from apps.inventory.models import Stock
        
        if not self.items.exists():
            return
        
        restoration_log = []
        
        for item in self.items.all():
            stock = Stock.objects.filter(product=item.product).first()
            
            if stock:
                old_qty = stock.quantity
                stock.quantity += item.quantity
                stock.save()
                
                restoration_log.append(
                    f"✓ {item.product.name}: {old_qty} → {stock.quantity} "
                    f"(restored {item.quantity} to {stock.warehouse.name})"
                )
            else:
                restoration_log.append(
                    f"⚠️ {item.product.name}: No stock record found to restore to"
                )
        
        # Print restoration log
        print(f"\n{'='*60}")
        print(f"Stock Restoration for Order #{self.id} (Cancelled)")
        print(f"{'='*60}")
        for log in restoration_log:
            print(log)
        print(f"{'='*60}\n")
        
        return restoration_log


class OrderItem(TrackableModel):
    """Order line items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "order_items"
        
    def save(self, *args, **kwargs):
        """Auto-calculate subtotal"""
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# Remove the pre_save signal - we handle this in admin now
# It was causing issues because it ran before items were saved
