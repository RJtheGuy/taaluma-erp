from rest_framework import serializers
from apps.accounts.models import User
from apps.inventory.models import Warehouse, Product, Stock
from apps.sales.models import Customer, Order, OrderItem
from apps.analytics.models import Prediction, SalesMetric
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal


# ============ ACCOUNTS SERIALIZERS ============

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration with password validation"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'role', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """User details (safe fields only)"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'first_name', 'last_name', 'full_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class PasswordChangeSerializer(serializers.Serializer):
    """Secure password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


# ============ INVENTORY SERIALIZERS ============

class WarehouseSerializer(serializers.ModelSerializer):
    """Warehouse CRUD"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    stock_count = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'is_active', 'created_at', 'updated_at', 'created_by_name', 'stock_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_stock_count(self, obj):
        return obj.stocks.count()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Warehouse name must be at least 2 characters.")
        return value.strip()


class ProductSerializer(serializers.ModelSerializer):
    """Product CRUD with price validation"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    total_stock = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'cost_price', 'selling_price', 
            'description', 'is_active', 'created_at', 'updated_at', 
            'created_by_name', 'total_stock', 'profit_margin'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_stock(self, obj):
        return sum(stock.quantity for stock in obj.stocks.all())

    def get_profit_margin(self, obj):
        if obj.cost_price > 0:
            margin = ((obj.selling_price - obj.cost_price) / obj.cost_price) * 100
            return round(margin, 2)
        return 0

    def validate_sku(self, value):
        value = value.strip().upper()
        if len(value) < 3:
            raise serializers.ValidationError("SKU must be at least 3 characters.")
        
        # Check uniqueness on update
        if self.instance:
            if Product.objects.exclude(pk=self.instance.pk).filter(sku=value).exists():
                raise serializers.ValidationError("Product with this SKU already exists.")
        return value

    def validate(self, attrs):
        cost_price = attrs.get('cost_price', self.instance.cost_price if self.instance else None)
        selling_price = attrs.get('selling_price', self.instance.selling_price if self.instance else None)

        if cost_price and selling_price:
            if cost_price < 0:
                raise serializers.ValidationError({"cost_price": "Cost price cannot be negative."})
            if selling_price < 0:
                raise serializers.ValidationError({"selling_price": "Selling price cannot be negative."})
            if selling_price < cost_price:
                raise serializers.ValidationError({
                    "selling_price": "Selling price should not be less than cost price."
                })
        
        return attrs


class StockSerializer(serializers.ModelSerializer):
    """Stock management with validation"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_low = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'warehouse', 
            'warehouse_name', 'quantity', 'reorder_level', 'is_low',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_low(self, obj):
        return obj.quantity <= obj.reorder_level

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_reorder_level(self, value):
        if value < 0:
            raise serializers.ValidationError("Reorder level cannot be negative.")
        return value

    def validate(self, attrs):
        product = attrs.get('product')
        warehouse = attrs.get('warehouse')

        # Check for duplicate stock entry (same product + warehouse)
        if not self.instance:  # Only on create
            if Stock.objects.filter(product=product, warehouse=warehouse).exists():
                raise serializers.ValidationError({
                    "non_field_errors": "Stock entry already exists for this product in this warehouse."
                })
        
        return attrs


# ============ SALES SERIALIZERS ============

class CustomerSerializer(serializers.ModelSerializer):
    """Customer CRUD"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'is_active',
            'created_at', 'updated_at', 'created_by_name', 'total_orders', 'total_spent'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_orders(self, obj):
        return obj.orders.count()

    def get_total_spent(self, obj):
        return sum(order.total for order in obj.orders.filter(status__in=['confirmed', 'shipped', 'delivered']))

    def validate_email(self, value):
        if value:
            value = value.lower().strip()
        return value

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Customer name must be at least 2 characters.")
        return value.strip()


class OrderItemSerializer(serializers.ModelSerializer):
    """Order line items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Order with nested items"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=False)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'status', 'total', 'notes',
            'items', 'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = ['id', 'total', 'created_at', 'updated_at']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total = Decimal('0.00')
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total += item.subtotal
        
        order.total = total
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update items if provided
        if items_data is not None:
            instance.items.all().delete()
            total = Decimal('0.00')
            for item_data in items_data:
                item = OrderItem.objects.create(order=instance, **item_data)
                total += item.subtotal
            instance.total = total
        
        instance.save()
        return instance


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order list"""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'status', 'total', 'items_count', 'created_at']
        read_only_fields = ['id', 'total', 'created_at']

    def get_items_count(self, obj):
        return obj.items.count()


# ============ ANALYTICS SERIALIZERS ============

class PredictionSerializer(serializers.ModelSerializer):
    """ML predictions"""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'product', 'product_name', 'date', 'predicted_quantity', 'confidence_score', 'model_version', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalesMetricSerializer(serializers.ModelSerializer):
    """Sales metrics"""
    class Meta:
        model = SalesMetric
        fields = ['id', 'date', 'total_sales', 'total_orders', 'metric_type', 'created_at']
        read_only_fields = ['id', 'created_at']
