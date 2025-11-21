from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.inventory.models import Warehouse, Product, Stock
from apps.sales.models import Customer, Order, OrderItem
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=20,
            help='Number of products to create'
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=10,
            help='Number of customers to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=30,
            help='Number of orders to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Generating sample data...')
        
        # Get or create admin user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@taalumaerp.com',
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin'
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin123)'))
        
        # Create warehouses
        warehouses = []
        for name, location in [
            ('Main Warehouse', 'Treviso, Italy'),
            ('Secondary Storage', 'Conegliano, Italy'),
            ('Distribution Center', 'Mestre, Italy')
        ]:
            wh, _ = Warehouse.objects.get_or_create(
                name=name,
                defaults={'location': location, 'created_by': user}
            )
            warehouses.append(wh)
        self.stdout.write(self.style.SUCCESS(f'Created {len(warehouses)} warehouses'))
        
        # Create products
        categories = ['Textiles', 'Food', 'Cosmetics', 'Crafts', 'Spices']
        products = []
        
        for i in range(options['products']):
            category = random.choice(categories)
            product, _ = Product.objects.get_or_create(
                sku=f'{category[:3].upper()}-{i+1:03d}',
                defaults={
                    'name': f'{category} Item {i+1}',
                    'category': category,
                    'cost_price': Decimal(str(random.uniform(5, 50))),
                    'selling_price': Decimal(str(random.uniform(10, 100))),
                    'description': f'Sample {category.lower()} product',
                    'created_by': user
                }
            )
            products.append(product)
            
            # Create stock for each warehouse
            for wh in warehouses:
                Stock.objects.get_or_create(
                    product=product,
                    warehouse=wh,
                    defaults={
                        'quantity': random.randint(10, 200),
                        'reorder_level': random.randint(5, 20),
                        'created_by': user
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        # Create customers
        customers = []
        for i in range(options['customers']):
            customer, _ = Customer.objects.get_or_create(
                email=f'customer{i+1}@example.com',
                defaults={
                    'name': f'Customer {i+1}',
                    'phone': f'+39 {random.randint(100,999)} {random.randint(100,999)} {random.randint(1000,9999)}',
                    'address': f'Via Test {i+1}, Treviso',
                    'created_by': user
                }
            )
            customers.append(customer)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(customers)} customers'))
        
        # Create orders
        statuses = ['pending', 'confirmed', 'shipped', 'delivered']
        for i in range(options['orders']):
            customer = random.choice(customers)
            status_choice = random.choice(statuses)
            
            order = Order.objects.create(
                customer=customer,
                status=status_choice,
                created_by=user
            )
            
            # Add 1-5 items per order
            total = Decimal('0.00')
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 10)
                
                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.selling_price,
                    created_by=user
                )
                total += item.subtotal
            
            order.total = total
            order.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created {options["orders"]} orders'))
        self.stdout.write(self.style.SUCCESS('Sample data generation complete!'))
