from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.inventory.models import Product, Warehouse, Stock
from apps.sales.models import Customer, Order

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test JWT authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_obtain_token(self):
        """Test obtaining JWT token"""
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_credentials(self):
        """Test with invalid credentials"""
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductAPITests(APITestCase):
    """Test Product API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='manager'
        )
        self.client.force_authenticate(user=self.user)
        
        self.product_data = {
            'name': 'Test Product',
            'sku': 'TEST-001',
            'category': 'Test',
            'cost_price': '10.00',
            'selling_price': '20.00'
        }
    
    def test_create_product(self):
        """Test creating a product"""
        response = self.client.post('/api/products/', self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(response.data['sku'], 'TEST-001')
    
    def test_list_products(self):
        """Test listing products"""
        Product.objects.create(created_by=self.user, **self.product_data)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_invalid_sku_length(self):
        """Test SKU validation"""
        data = self.product_data.copy()
        data['sku'] = 'AB'  # Too short
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StockAPITests(APITestCase):
    """Test Stock API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='inventory_manager'
        )
        self.client.force_authenticate(user=self.user)
        
        self.warehouse = Warehouse.objects.create(
            name='Main Warehouse',
            location='Test Location',
            created_by=self.user
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            category='Test',
            cost_price='10.00',
            selling_price='20.00',
            created_by=self.user
        )
    
    def test_create_stock(self):
        """Test creating stock entry"""
        response = self.client.post('/api/stocks/', {
            'product': str(self.product.id),
            'warehouse': str(self.warehouse.id),
            'quantity': 100,
            'reorder_level': 10
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_adjust_quantity(self):
        """Test adjusting stock quantity"""
        stock = Stock.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantity=50,
            created_by=self.user
        )
        
        response = self.client.post(
            f'/api/stocks/{stock.id}/adjust_quantity/',
            {'adjustment': 10}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stock.refresh_from_db()
        self.assertEqual(stock.quantity, 60)


class OrderAPITests(APITestCase):
    """Test Order API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff'
        )
        self.client.force_authenticate(user=self.user)
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='customer@test.com',
            created_by=self.user
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            category='Test',
            cost_price='10.00',
            selling_price='20.00',
            created_by=self.user
        )
    
    def test_create_order(self):
        """Test creating an order"""
        response = self.client.post('/api/orders/', {
            'customer': str(self.customer.id),
            'status': 'pending',
            'items': [
                {
                    'product': str(self.product.id),
                    'quantity': 5,
                    'price': '20.00'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total'], '100.00')


class PermissionTests(APITestCase):
    """Test role-based permissions"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            role='admin',
            is_staff=True
        )
        
        self.staff = User.objects.create_user(
            username='staff',
            password='staffpass',
            role='staff'
        )
    
    def test_staff_cannot_view_analytics(self):
        """Test that staff cannot access analytics"""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/metrics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_view_analytics(self):
        """Test that admin can access analytics"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/metrics/')
        # Will be 200 or 404 depending on data, but not 403
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# To run tests:
# python manage.py test apps.api.tests
