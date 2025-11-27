# # sales/models.py
# from django.db import models
# from apps.core.models import BaseModel
# from apps.inventory.models import Product, Warehouse, Stock


# class Customer(BaseModel):
#     name = models.CharField(max_length=255)
#     email = models.EmailField(blank=True, null=True)
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'customers'  # Match your migration!
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.name


# class Order(BaseModel):
#     customer = models.ForeignKey(
#         Customer, 
#         on_delete=models.SET_NULL, 
#         null=True,
#         related_name='orders'
#     )
#     warehouse = models.ForeignKey(
#         Warehouse,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='orders',
#         help_text="Warehouse fulfilling this order"
#     )
#     total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     status = models.CharField(
#         max_length=50,
#         choices=[
#             ('pending', 'Pending'),
#             ('confirmed', 'Confirmed'),
#             ('shipped', 'Shipped'),
#             ('delivered', 'Delivered'),
#             ('cancelled', 'Cancelled'),
#         ],
#         default='pending'
#     )
#     notes = models.TextField(blank=True, null=True)
    
#     class Meta:
#         db_table = 'orders'  # Match your migration!
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"Order #{str(self.id)[:8]} - {self.customer.name if self.customer else 'No Customer'}"
    
#     def calculate_total(self):
#         """Calculate order total from items"""
#         total = sum(item.subtotal for item in self.items.all())
#         self.total = total
#         self.save()
#         return total
    
#     def deduct_stock(self):
#         """Deduct stock from warehouse when order is confirmed"""
#         if not self.warehouse:
#             return False
        
#         for item in self.items.all():
#             try:
#                 stock = Stock.objects.get(
#                     product=item.product,
#                     warehouse=self.warehouse
#                 )
#                 stock.quantity -= item.quantity
#                 stock.save()
#             except Stock.DoesNotExist:
#                 pass
        
#         return True
    
#     def restore_stock(self):
#         """Restore stock to warehouse when order is cancelled"""
#         if not self.warehouse:
#             return False
        
#         for item in self.items.all():
#             try:
#                 stock = Stock.objects.get(
#                     product=item.product,
#                     warehouse=self.warehouse
#                 )
#                 stock.quantity += item.quantity
#                 stock.save()
#             except Stock.DoesNotExist:
#                 pass
        
#         return True


# class OrderItem(BaseModel):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
#     class Meta:
#         db_table = 'order_items'  # Match your migration!
    
#     def __str__(self):
#         return f"{self.product.name} x {self.quantity}"
    
#     def save(self, *args, **kwargs):
#         """Auto-calculate subtotal before saving"""
#         self.subtotal = self.quantity * self.price
#         super().save(*args, **kwargs)

# apps/sales/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel
from apps.inventory.models import Product, Warehouse, Stock


class Customer(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'customers'
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
    
    # Keep this field for database compatibility (not used in logic)
    is_locked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{str(self.id)[:8]} - {self.customer.name if self.customer else 'No Customer'}"
    
    def clean(self, user=None):
        """
        Validate order before saving
        Check stock availability with permission-aware messages
        """
        super().clean()
        
        # Only validate stock for confirmed orders
        if self.status != 'confirmed':
            return
        
        # Skip validation for new orders (no items yet)
        if not self.pk:
            return
        
        # Get all items in this order
        items = self.items.all()
        
        insufficient_stock = []
        alternatives = []
        user_can_see_details = True
        
        # Check if user has warehouse restrictions
        if user and hasattr(user, 'assigned_warehouse') and user.assigned_warehouse:
            user_can_see_details = False
        
        for item in items:
            # Check stock at selected warehouse
            try:
                stock = Stock.objects.get(
                    product=item.product,
                    warehouse=self.warehouse
                )
                
                if stock.quantity < item.quantity:
                    # Insufficient stock!
                    insufficient_stock.append({
                        'product': item.product.name,
                        'requested': item.quantity,
                        'available': stock.quantity,
                        'shortage': item.quantity - stock.quantity
                    })
                    
                    # Find alternative warehouses with stock
                    alternative_stocks = Stock.objects.filter(
                        product=item.product,
                        quantity__gte=item.quantity
                    ).exclude(
                        warehouse=self.warehouse
                    ).select_related('warehouse')
                    
                    if alternative_stocks.exists():
                        alternatives.append({
                            'product': item.product.name,
                            'count': alternative_stocks.count(),
                            'warehouses': [
                                {
                                    'name': alt.warehouse.name,
                                    'available': alt.quantity
                                }
                                for alt in alternative_stocks
                            ] if user_can_see_details else []
                        })
            
            except Stock.DoesNotExist:
                # Product doesn't exist at this warehouse
                insufficient_stock.append({
                    'product': item.product.name,
                    'requested': item.quantity,
                    'available': 0,
                    'shortage': item.quantity
                })
                
                # Find where it IS available
                alternative_stocks = Stock.objects.filter(
                    product=item.product,
                    quantity__gte=item.quantity
                ).select_related('warehouse')
                
                if alternative_stocks.exists():
                    alternatives.append({
                        'product': item.product.name,
                        'count': alternative_stocks.count(),
                        'warehouses': [
                            {
                                'name': alt.warehouse.name,
                                'available': alt.quantity
                            }
                            for alt in alternative_stocks
                        ] if user_can_see_details else []
                    })
        
        # If insufficient stock found, raise validation error
        if insufficient_stock:
            error_message = self._build_error_message(
                insufficient_stock, 
                alternatives, 
                user_can_see_details
            )
            raise ValidationError(error_message)
    
    def _build_error_message(self, insufficient_stock, alternatives, show_details):
        """
        Build error message based on user permissions
        OPTION B: Restricted users see "available elsewhere" without details
        """
        error_message = "❌ Cannot create order - Insufficient stock:\n\n"
        
        # Show what's missing
        for item in insufficient_stock:
            error_message += f"• {item['product']}: "
            error_message += f"Requested {item['requested']} units, "
            
            if item['available'] > 0:
                error_message += f"only {item['available']} available at {self.warehouse.name} "
                error_message += f"(shortage: {item['shortage']} units)\n"
            else:
                error_message += f"not available at {self.warehouse.name}\n"
        
        # Show alternatives based on permissions
        if alternatives:
            if show_details:
                # ADMIN/SUPERUSER: Show full details
                error_message += "\n✅ Available at other warehouses:\n\n"
                for alt in alternatives:
                    error_message += f"📦 {alt['product']}:\n"
                    for wh in alt['warehouses']:
                        error_message += f"  • {wh['name']}: {wh['available']} units available\n"
                    error_message += "\n"
                
                error_message += "💡 Suggestion: Change warehouse in the dropdown above."
            
            else:
                # RESTRICTED USER: Show limited info (OPTION B)
                error_message += "\nℹ️ Information:\n\n"
                for alt in alternatives:
                    if alt['count'] == 1:
                        error_message += f"• {alt['product']} IS available at 1 other company location\n"
                    else:
                        error_message += f"• {alt['product']} IS available at {alt['count']} other company locations\n"
                
                error_message += "\n💡 Actions you can take:\n"
                error_message += "  1. Contact admin to check other warehouses\n"
                error_message += "  2. Call other warehouse managers to arrange transfer\n"
                error_message += "  3. Contact supplier to restock your warehouse\n"
                error_message += "  4. Choose different product for customer\n"
        
        else:
            # No alternatives anywhere
            error_message += "\n❌ This product is not available at ANY warehouse.\n"
            error_message += "💡 Suggestion: Contact supplier or choose different product."
        
        return error_message
    
    def save(self, *args, user=None, **kwargs):
        """
        Override save to validate stock
        """
        # Run validation (checks stock availability)
        self.clean(user=user)
        
        super().save(*args, **kwargs)
        
        # Calculate total
        self.calculate_total()
    
    def calculate_total(self):
        """Calculate order total from items"""
        total = sum(item.subtotal for item in self.items.all())
        if self.total != total:
            self.total = total
            Order.objects.filter(pk=self.pk).update(total=total)
    
    def deduct_stock(self):
        """Deduct stock from warehouse when order is confirmed"""
        if not self.warehouse:
            return False
        
        with transaction.atomic():
            for item in self.items.all():
                try:
                    stock = Stock.objects.select_for_update().get(
                        product=item.product,
                        warehouse=self.warehouse
                    )
                    
                    if stock.quantity < item.quantity:
                        raise ValidationError(
                            f"❌ Cannot deduct stock for {item.product.name} - "
                            f"Insufficient quantity"
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
        
        with transaction.atomic():
            for item in self.items.all():
                try:
                    stock = Stock.objects.select_for_update().get(
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
        db_table = 'order_items'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate subtotal before saving"""
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
        # Update order total
        if self.order_id:
            self.order.calculate_total()
