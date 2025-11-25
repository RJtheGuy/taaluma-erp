from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User
from apps.inventory.models import Warehouse, Product, Stock
from apps.sales.models import Customer, Order, OrderItem
from apps.analytics.models import Prediction, SalesMetric

from .serializers import (
    UserSerializer, UserRegistrationSerializer, PasswordChangeSerializer,
    WarehouseSerializer, ProductSerializer, StockSerializer,
    CustomerSerializer, OrderSerializer, OrderListSerializer, OrderItemSerializer,
    PredictionSerializer, SalesMetricSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsManagerOrAdmin, CanManageInventory, 
    CanManageSales, CanViewAnalytics
)


# ============ ACCOUNTS VIEWSETS ============

class UserViewSet(viewsets.ModelViewSet):
    """User management with registration"""
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============ INVENTORY VIEWSETS ============

class WarehouseViewSet(viewsets.ModelViewSet):
    """Warehouse CRUD"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, CanManageInventory]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def stock_levels(self, request, pk=None):
        """Get all stock levels for this warehouse"""
        warehouse = self.get_object()
        stocks = Stock.objects.filter(warehouse=warehouse).select_related('product')
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """Product CRUD with search and filters"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, CanManageInventory]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'sku', 'selling_price', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        low_stock_ids = Stock.objects.filter(
            quantity__lte=F('reorder_level')
        ).values_list('product_id', flat=True)
        
        products = self.queryset.filter(id__in=low_stock_ids)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock_summary(self, request, pk=None):
        """Get stock summary across all warehouses"""
        product = self.get_object()
        stocks = product.stocks.all().select_related('warehouse')
        
        summary = {
            'product': ProductSerializer(product).data,
            'total_quantity': sum(s.quantity for s in stocks),
            'warehouses': StockSerializer(stocks, many=True).data
        }
        return Response(summary)


class StockViewSet(viewsets.ModelViewSet):
    """Stock management"""
    queryset = Stock.objects.all().select_related('product', 'warehouse')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated, CanManageInventory]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'product']
    ordering_fields = ['quantity', 'created_at']
    ordering = ['product__name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def adjust_quantity(self, request, pk=None):
        """Adjust stock quantity (add or subtract)"""
        stock = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        
        try:
            adjustment = int(adjustment)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid adjustment value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_quantity = stock.quantity + adjustment
        
        if new_quantity < 0:
            return Response(
                {'error': 'Insufficient stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock.quantity = new_quantity
        stock.updated_by = request.user
        stock.save()
        
        serializer = self.get_serializer(stock)
        return Response(serializer.data)


# ============ SALES VIEWSETS ============

class CustomerViewSet(viewsets.ModelViewSet):
    """Customer management"""
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, CanManageSales]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get all orders for this customer"""
        customer = self.get_object()
        orders = customer.orders.all()
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    """Order management with status workflow"""
    queryset = Order.objects.all().select_related('customer')
    permission_classes = [IsAuthenticated, CanManageSales]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(created_by=self.request.user)
        
        # Auto-deduct stock when order is confirmed
        if order.status == 'confirmed':
            self._deduct_stock(order)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        order = serializer.save(updated_by=self.request.user)
        
        # Handle stock deduction on status change to confirmed
        if old_status != 'confirmed' and order.status == 'confirmed':
            self._deduct_stock(order)

    def _deduct_stock(self, order):
        """Deduct stock when order is confirmed"""
        for item in order.items.all():
            # Try to find stock in any warehouse
            stock = Stock.objects.filter(
                product=item.product, 
                quantity__gte=item.quantity
            ).first()
            
            if stock:
                stock.quantity -= item.quantity
                stock.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        if order.status == 'cancelled':
            return Response(
                {'error': 'Order already cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.updated_by = request.user
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        stats = {
            'total': self.queryset.count(),
            'pending': self.queryset.filter(status='pending').count(),
            'confirmed': self.queryset.filter(status='confirmed').count(),
            'shipped': self.queryset.filter(status='shipped').count(),
            'delivered': self.queryset.filter(status='delivered').count(),
            'cancelled': self.queryset.filter(status='cancelled').count(),
            'total_revenue': self.queryset.filter(
                status__in=['confirmed', 'shipped', 'delivered']
            ).aggregate(total=Sum('total'))['total'] or 0
        }
        return Response(stats)


# ============ ANALYTICS VIEWSETS ============

class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """View predictions (read-only, generated by ML tasks)"""
    queryset = Prediction.objects.all().select_related('product')
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'date']
    ordering_fields = ['date', 'predicted_quantity']
    ordering = ['-date']


class SalesMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """View sales metrics"""
    queryset = SalesMetric.objects.all()
    serializer_class = SalesMetricSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['metric_type', 'date']
    ordering_fields = ['date']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def last_30_days(self, request):
        """Get metrics for last 30 days"""
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        metrics = self.queryset.filter(
            date__gte=thirty_days_ago,
            metric_type='daily'
        )
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)
