# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType
# from apps.inventory.models import Warehouse, Product, Stock
# from apps.sales.models import Customer, Order, OrderItem
# from decimal import Decimal
# import random

# User = get_user_model()


# class Command(BaseCommand):
#     help = 'Generate complete test data including users, groups, warehouses, products, and orders'
    
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--products',
#             type=int,
#             default=50,
#             help='Number of products to create'
#         )
#         parser.add_argument(
#             '--customers',
#             type=int,
#             default=15,
#             help='Number of customers to create'
#         )
#         parser.add_argument(
#             '--orders',
#             type=int,
#             default=50,
#             help='Number of orders to create'
#         )
    
#     def handle(self, *args, **options):
#         self.stdout.write(self.style.WARNING('=' * 70))
#         self.stdout.write(self.style.WARNING('🚀 GENERATING COMPLETE TEST DATA FOR ETHNIC WORLD ERP'))
#         self.stdout.write(self.style.WARNING('=' * 70))
        
#         # Step 1: Create Groups
#         self.stdout.write('\n📋 Step 1: Creating User Groups...')
#         groups = self.create_groups()
        
#         # Step 2: Create Warehouses
#         self.stdout.write('\n🏢 Step 2: Creating Warehouses...')
#         warehouses = self.create_warehouses()
        
#         # Step 3: Create Users with Roles
#         self.stdout.write('\n👥 Step 3: Creating Users with Role Assignments...')
#         users = self.create_users(warehouses, groups)
        
#         # Step 4: Create Products
#         self.stdout.write(f'\n📦 Step 4: Creating {options["products"]} Products...')
#         products = self.create_products(options['products'], users['admin'])
        
#         # Step 5: Create Stock Records
#         self.stdout.write('\n📊 Step 5: Creating Stock Records...')
#         self.create_stock(products, warehouses, users['admin'])
        
#         # Step 6: Create Customers
#         self.stdout.write(f'\n🛒 Step 6: Creating {options["customers"]} Customers...')
#         customers = self.create_customers(options['customers'], users['admin'])
        
#         # Step 7: Create Orders
#         self.stdout.write(f'\n📝 Step 7: Creating {options["orders"]} Orders...')
#         self.create_orders(options['orders'], customers, products, warehouses, users)
        
#         # Step 8: Print Summary
#         self.print_summary(users, warehouses)
        
#         self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
#         self.stdout.write(self.style.SUCCESS('✅ TEST DATA GENERATION COMPLETE!'))
#         self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
    
#     def create_groups(self):
#         """Create user groups with permissions"""
#         groups = {}
        
#         group_configs = [
#             {
#                 'name': 'OWNER (Client Admin)',
#                 'permissions': ['view', 'add', 'change', 'delete'],  # Full access
#                 'models': ['warehouse', 'product', 'stock', 'customer', 'order', 'orderitem', 'user']
#             },
#             {
#                 'name': 'GENERAL MANAGER (Multi-location oversight)',
#                 'permissions': ['view', 'add', 'change', 'delete'],
#                 'models': ['warehouse', 'product', 'stock', 'customer', 'order', 'orderitem']
#             },
#             {
#                 'name': 'STORE MANAGER (Location-specific)',
#                 'permissions': ['view', 'add', 'change'],
#                 'models': ['product', 'stock', 'customer', 'order', 'orderitem']
#             },
#             {
#                 'name': 'STORE STAFF (Order entry)',
#                 'permissions': ['view', 'add'],
#                 'models': ['customer', 'order', 'orderitem']
#             },
#             {
#                 'name': 'INVENTORY MANAGER (All locations)',
#                 'permissions': ['view', 'add', 'change'],
#                 'models': ['warehouse', 'product', 'stock']
#             },
#         ]
        
#         for config in group_configs:
#             group, created = Group.objects.get_or_create(name=config['name'])
            
#             if created:
#                 # Add permissions to group
#                 for model_name in config['models']:
#                     for perm_type in config['permissions']:
#                         try:
#                             permission = Permission.objects.get(
#                                 codename=f'{perm_type}_{model_name}'
#                             )
#                             group.permissions.add(permission)
#                         except Permission.DoesNotExist:
#                             pass
                
#                 self.stdout.write(f'  ✓ Created group: {config["name"]}')
#             else:
#                 self.stdout.write(f'  • Group exists: {config["name"]}')
            
#             groups[config['name']] = group
        
#         return groups
    
#     def create_warehouses(self):
#         """Create three Ethnic World warehouses"""
#         warehouses = []
        
#         warehouse_data = [
#             {
#                 'name': 'Ethnic World Conegliano',
#                 'location': 'Via Zanella 130, 31015 Conegliano TV, Italy'
#             },
#             {
#                 'name': 'Ethnic World Vicenza',
#                 'location': 'Viale Milano 37, 36100 Vicenza VI, Italy'
#             },
#             {
#                 'name': 'Ethnic World Padova',
#                 'location': 'Via Venezia 45, 35131 Padova PD, Italy'
#             }
#         ]
        
#         for data in warehouse_data:
#             warehouse, created = Warehouse.objects.get_or_create(
#                 name=data['name'],
#                 defaults={'location': data['location']}
#             )
#             warehouses.append(warehouse)
            
#             if created:
#                 self.stdout.write(f'  ✓ Created: {data["name"]}')
#             else:
#                 self.stdout.write(f'  • Exists: {data["name"]}')
        
#         return warehouses
    
#     def create_users(self, warehouses, groups):
#         """Create users with proper roles and warehouse assignments"""
#         users = {}
        
#         user_data = [
#             # Superuser/Admin
#             {
#                 'username': 'admin',
#                 'email': 'admin@ethnicworld.it',
#                 'password': 'admin123',
#                 'first_name': 'Admin',
#                 'last_name': 'User',
#                 'role': 'admin',
#                 'is_staff': True,
#                 'is_superuser': True,
#                 'warehouse': None,
#                 'groups': []
#             },
#             # Owner
#             {
#                 'username': 'owner.ethnicworld',
#                 'email': 'owner@ethnicworld.it',
#                 'password': 'owner123',
#                 'first_name': 'Mario',
#                 'last_name': 'Rossi',
#                 'role': 'owner',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': None,
#                 'groups': ['OWNER (Client Admin)']
#             },
#             # General Manager
#             {
#                 'username': 'manager.general',
#                 'email': 'general@ethnicworld.it',
#                 'password': 'manager123',
#                 'first_name': 'Luigi',
#                 'last_name': 'Bianchi',
#                 'role': 'general_manager',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': None,
#                 'groups': ['GENERAL MANAGER (Multi-location oversight)']
#             },
#             # Inventory Manager
#             {
#                 'username': 'inventory.ethnicworld',
#                 'email': 'inventory@ethnicworld.it',
#                 'password': 'inventory123',
#                 'first_name': 'Giuseppe',
#                 'last_name': 'Verdi',
#                 'role': 'inventory_manager',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': None,
#                 'groups': ['INVENTORY MANAGER (All locations)']
#             },
#             # Conegliano - Store Manager
#             {
#                 'username': 'manager.conegliano',
#                 'email': 'conegliano.manager@ethnicworld.it',
#                 'password': 'manager123',
#                 'first_name': 'Antonio',
#                 'last_name': 'Ferrari',
#                 'role': 'store_manager',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[0],  # Conegliano
#                 'groups': ['STORE MANAGER (Location-specific)']
#             },
#             # Conegliano - Staff 1
#             {
#                 'username': 'staff1.conegliano',
#                 'email': 'staff1.conegliano@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Marco',
#                 'last_name': 'Romano',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[0],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#             # Conegliano - Staff 2
#             {
#                 'username': 'staff2.conegliano',
#                 'email': 'staff2.conegliano@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Giulia',
#                 'last_name': 'Russo',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[0],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#             # Vicenza - Store Manager
#             {
#                 'username': 'manager.vicenza',
#                 'email': 'vicenza.manager@ethnicworld.it',
#                 'password': 'manager123',
#                 'first_name': 'Francesco',
#                 'last_name': 'Ricci',
#                 'role': 'store_manager',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[1],  # Vicenza
#                 'groups': ['STORE MANAGER (Location-specific)']
#             },
#             # Vicenza - Staff 1
#             {
#                 'username': 'staff1.vicenza',
#                 'email': 'staff1.vicenza@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Alessia',
#                 'last_name': 'Colombo',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[1],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#             # Vicenza - Staff 2
#             {
#                 'username': 'staff2.vicenza',
#                 'email': 'staff2.vicenza@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Luca',
#                 'last_name': 'Esposito',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[1],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#             # Padova - Store Manager
#             {
#                 'username': 'manager.padova',
#                 'email': 'padova.manager@ethnicworld.it',
#                 'password': 'manager123',
#                 'first_name': 'Simone',
#                 'last_name': 'Moretti',
#                 'role': 'store_manager',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[2],  # Padova
#                 'groups': ['STORE MANAGER (Location-specific)']
#             },
#             # Padova - Staff 1
#             {
#                 'username': 'staff1.padova',
#                 'email': 'staff1.padova@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Chiara',
#                 'last_name': 'Bruno',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[2],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#             # Padova - Staff 2
#             {
#                 'username': 'staff2.padova',
#                 'email': 'staff2.padova@ethnicworld.it',
#                 'password': 'staff123',
#                 'first_name': 'Andrea',
#                 'last_name': 'Gallo',
#                 'role': 'store_staff',
#                 'is_staff': True,
#                 'is_superuser': False,
#                 'warehouse': warehouses[2],
#                 'groups': ['STORE STAFF (Order entry)']
#             },
#         ]
        
#         for data in user_data:
#             user, created = User.objects.get_or_create(
#                 username=data['username'],
#                 defaults={
#                     'email': data['email'],
#                     'first_name': data['first_name'],
#                     'last_name': data['last_name'],
#                     'role': data['role'],
#                     'is_staff': data['is_staff'],
#                     'is_superuser': data['is_superuser'],
#                     'assigned_warehouse': data['warehouse']
#                 }
#             )
            
#             if created:
#                 user.set_password(data['password'])
                
#                 # Add to groups
#                 for group_name in data['groups']:
#                     if group_name in groups:
#                         user.groups.add(groups[group_name])
                
#                 user.save()
                
#                 warehouse_name = data['warehouse'].name if data['warehouse'] else 'All Locations'
#                 self.stdout.write(
#                     f'  ✓ Created: {data["username"]} ({data["role"]}) - {warehouse_name}'
#                 )
#             else:
#                 self.stdout.write(f'  • Exists: {data["username"]}')
            
#             users[data['username']] = user
        
#         return users
    
#     def create_products(self, count, admin_user):
#         """Create diverse ethnic products"""
#         products = []
        
#         product_categories = {
#             'Textiles': [
#                 'Sari Silk', 'Batik Fabric', 'Kente Cloth', 'Ikat Textile',
#                 'Mud Cloth', 'Embroidered Cotton', 'Block Print Fabric'
#             ],
#             'Spices': [
#                 'Turmeric Powder', 'Cardamom Pods', 'Saffron Threads', 'Curry Blend',
#                 'Garam Masala', 'Cumin Seeds', 'Coriander Powder'
#             ],
#             'Cosmetics': [
#                 'Argan Oil', 'Shea Butter', 'Henna Powder', 'Black Soap',
#                 'Rose Water', 'Kohl Eyeliner', 'Sandalwood Paste'
#             ],
#             'Crafts': [
#                 'Wooden Mask', 'Clay Pottery', 'Beaded Jewelry', 'Brass Statue',
#                 'Woven Basket', 'Leather Pouf', 'Carved Box'
#             ],
#             'Food': [
#                 'Basmati Rice', 'Chickpea Flour', 'Coconut Oil', 'Palm Oil',
#                 'Tamarind Paste', 'Date Syrup', 'Cassava Flour'
#             ]
#         }
        
#         idx = 1
#         for category, items in product_categories.items():
#             for item_name in items:
#                 if idx > count:
#                     break
                
#                 sku = f'{category[:3].upper()}-{idx:03d}'
#                 cost = Decimal(str(round(random.uniform(3, 40), 2)))
#                 selling = Decimal(str(round(float(cost) * random.uniform(1.5, 2.5), 2)))
                
#                 product, created = Product.objects.get_or_create(
#                     sku=sku,
#                     defaults={
#                         'name': item_name,
#                         'category': category,
#                         'cost_price': cost,
#                         'selling_price': selling,
#                         'description': f'Authentic {item_name.lower()} imported from origin'
#                     }
#                 )
                
#                 products.append(product)
                
#                 if created:
#                     self.stdout.write(f'  ✓ {sku}: {item_name} (€{selling})')
                
#                 idx += 1
                
#                 if idx > count:
#                     break
        
#         return products
    
#     def create_stock(self, products, warehouses, admin_user):
#         """Create stock records for all products in all warehouses"""
#         stock_count = 0
        
#         for product in products:
#             for warehouse in warehouses:
#                 quantity = random.randint(20, 300)
#                 reorder = random.randint(10, 30)
                
#                 stock, created = Stock.objects.get_or_create(
#                     product=product,
#                     warehouse=warehouse,
#                     defaults={
#                         'quantity': quantity,
#                         'reorder_level': reorder
#                     }
#                 )
                
#                 if created:
#                     stock_count += 1
        
#         self.stdout.write(f'  ✓ Created {stock_count} stock records across {len(warehouses)} warehouses')
    
#     def create_customers(self, count, admin_user):
#         """Create customer records"""
#         customers = []
        
#         italian_names = [
#             ('Giovanni', 'Romano'), ('Maria', 'Rizzo'), ('Giuseppe', 'Fontana'),
#             ('Anna', 'Marino'), ('Francesco', 'Greco'), ('Laura', 'Bruno'),
#             ('Alessandro', 'Galli'), ('Sofia', 'Conti'), ('Matteo', 'De Luca'),
#             ('Chiara', 'Costa'), ('Lorenzo', 'Giordano'), ('Valentina', 'Mancini'),
#             ('Davide', 'Lombardi'), ('Elena', 'Barbieri'), ('Simone', 'Rossetti')
#         ]
        
#         for i in range(count):
#             first_name, last_name = random.choice(italian_names)
            
#             customer, created = Customer.objects.get_or_create(
#                 email=f'{first_name.lower()}.{last_name.lower()}{i+1}@example.it',
#                 defaults={
#                     'name': f'{first_name} {last_name}',
#                     'phone': f'+39 3{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}',
#                     'address': f'Via {random.choice(["Roma", "Milano", "Venezia", "Dante"])} {random.randint(1,150)}, {random.choice(["Treviso", "Padova", "Vicenza"])} TV, Italy'
#                 }
#             )
            
#             customers.append(customer)
            
#             if created:
#                 self.stdout.write(f'  ✓ Customer: {customer.name}')
        
#         return customers
    
#     def create_orders(self, count, customers, products, warehouses, users):
#         """Create orders distributed across warehouses"""
#         statuses = ['pending', 'confirmed', 'shipped', 'delivered']
#         status_weights = [0.2, 0.3, 0.3, 0.2]  # More confirmed/shipped orders
        
#         for i in range(count):
#             customer = random.choice(customers)
#             warehouse = random.choice(warehouses)
#             status = random.choices(statuses, weights=status_weights)[0]
            
#             order = Order.objects.create(
#                 customer=customer,
#                 warehouse=warehouse,
#                 status=status
#             )
            
#             # Add 1-5 items per order
#             num_items = random.randint(1, 5)
#             order_products = random.sample(products, min(num_items, len(products)))
            
#             for product in order_products:
#                 quantity = random.randint(1, 10)
                
#                 OrderItem.objects.create(
#                     order=order,
#                     product=product,
#                     quantity=quantity,
#                     price=product.selling_price
#                 )
            
#             # Calculate total
#             order.calculate_total()
            
#             # Deduct stock if order is confirmed/shipped/delivered
#             if status in ['confirmed', 'shipped', 'delivered']:
#                 order.deduct_stock()
            
#             if (i + 1) % 10 == 0:
#                 self.stdout.write(f'  ✓ Created {i + 1}/{count} orders...')
        
#         self.stdout.write(f'  ✓ All {count} orders created successfully')
    
#     def print_summary(self, users, warehouses):
#         """Print comprehensive summary"""
#         self.stdout.write('\n' + '=' * 70)
#         self.stdout.write(self.style.SUCCESS('📊 TEST DATA SUMMARY'))
#         self.stdout.write('=' * 70)
        
#         self.stdout.write('\n🏢 WAREHOUSES:')
#         for wh in warehouses:
#             self.stdout.write(f'  • {wh.name}')
        
#         self.stdout.write('\n👥 USER ACCOUNTS (username / password / warehouse):')
#         self.stdout.write(f'  • admin / admin123 / All Locations [SUPERUSER]')
#         self.stdout.write(f'  • owner.ethnicworld / owner123 / All Locations')
#         self.stdout.write(f'  • manager.general / manager123 / All Locations')
#         self.stdout.write(f'  • inventory.ethnicworld / inventory123 / All Locations')
#         self.stdout.write(f'  • manager.conegliano / manager123 / Conegliano')
#         self.stdout.write(f'  • staff1.conegliano / staff123 / Conegliano')
#         self.stdout.write(f'  • staff2.conegliano / staff123 / Conegliano')
#         self.stdout.write(f'  • manager.vicenza / manager123 / Vicenza')
#         self.stdout.write(f'  • staff1.vicenza / staff123 / Vicenza')
#         self.stdout.write(f'  • staff2.vicenza / staff123 / Vicenza')
#         self.stdout.write(f'  • manager.padova / manager123 / Padova')
#         self.stdout.write(f'  • staff1.padova / staff123 / Padova')
#         self.stdout.write(f'  • staff2.padova / staff123 / Padova')
        
#         self.stdout.write('\n📦 DATABASE STATS:')
#         self.stdout.write(f'  • Products: {Product.objects.count()}')
#         self.stdout.write(f'  • Stock Records: {Stock.objects.count()}')
#         self.stdout.write(f'  • Customers: {Customer.objects.count()}')
#         self.stdout.write(f'  • Orders: {Order.objects.count()}')
#         self.stdout.write(f'  • Order Items: {OrderItem.objects.count()}')
        
#         self.stdout.write('\n🧪 TESTING RECOMMENDATIONS:')
#         self.stdout.write('  1. Login as admin to see full system')
#         self.stdout.write('  2. Login as manager.padova to test warehouse isolation')
#         self.stdout.write('  3. Create test order to verify stock deduction')
#         self.stdout.write('  4. Check different user permissions')
        
#         self.stdout.write('\n🌐 ADMIN URL:')
#         self.stdout.write('  https://taaluma-erp-production.up.railway.app/admin/')



from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from apps.accounts.models import Organization
from apps.inventory.models import Warehouse, Product, Stock
from apps.sales.models import Customer, Order, OrderItem
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate complete test data including organizations, users, groups, warehouses, products, and orders'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of products to create'
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=15,
            help='Number of customers to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=50,
            help='Number of orders to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('🚀 GENERATING COMPLETE TEST DATA FOR TAALUMA ERP'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        with transaction.atomic():
            # Step 0: Create Organizations
            self.stdout.write('\n🏢 Step 0: Creating Organizations...')
            organizations = self.create_organizations()
            
            # Step 1: Create Groups
            self.stdout.write('\n📋 Step 1: Creating User Groups...')
            groups = self.create_groups()
            
            # Step 2: Create Warehouses
            self.stdout.write('\n🏭 Step 2: Creating Warehouses...')
            warehouses = self.create_warehouses(organizations)
            
            # Step 3: Create Users with Roles
            self.stdout.write('\n👥 Step 3: Creating Users with Role Assignments...')
            users = self.create_users(organizations, warehouses, groups)
            
            # Step 4: Create Products
            self.stdout.write(f'\n📦 Step 4: Creating {options["products"]} Products...')
            products = self.create_products(options['products'], users, organizations)
            
            # Step 5: Create Stock Records
            self.stdout.write('\n📊 Step 5: Creating Stock Records...')
            self.create_stock(products, warehouses, users)
            
            # Step 6: Create Customers
            self.stdout.write(f'\n🛒 Step 6: Creating {options["customers"]} Customers...')
            customers = self.create_customers(options['customers'], users, organizations)
            
            # Step 7: Create Orders
            self.stdout.write(f'\n📝 Step 7: Creating {options["orders"]} Orders...')
            self.create_orders(options['orders'], customers, products, warehouses, users)
            
            # Step 8: Print Summary
            self.print_summary(organizations, users, warehouses)
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ TEST DATA GENERATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('=' * 70 + '\n'))
    
    def create_organizations(self):
        """Create test organizations"""
        organizations = {}
        
        org_data = [
            {
                'slug': 'ethnic-world',
                'name': 'Ethnic World Import/Export',
                'subscription_status': 'active',
                'monthly_fee': Decimal('600.00'),
                'contact_email': 'info@ethnicworld.it',
                'contact_phone': '+39 0438 123456',
                'address': 'Via Zanella 130, 31015 Conegliano TV, Italy',
            },
            {
                'slug': 'african-heritage',
                'name': 'African Heritage Traders',
                'subscription_status': 'active',
                'monthly_fee': Decimal('300.00'),
                'contact_email': 'contact@africanheritage.com',
                'contact_phone': '+39 049 555 0000',
                'address': 'Via Venezia 45, 35131 Padova PD, Italy',
            },
            {
                'slug': 'demo-company',
                'name': 'Demo Import/Export Ltd',
                'subscription_status': 'trial',
                'monthly_fee': Decimal('300.00'),
                'contact_email': 'demo@example.com',
                'contact_phone': '+39 123 456 7890',
                'address': 'Via Demo 123, Milano, Italy',
            }
        ]
        
        for data in org_data:
            org, created = Organization.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            organizations[data['slug']] = org
            
            if created:
                self.stdout.write(f'  ✓ Created: {data["name"]} ({data["subscription_status"]})')
            else:
                self.stdout.write(f'  • Exists: {data["name"]}')
        
        return organizations
    
    def create_groups(self):
        """Create user groups with permissions"""
        groups = {}
        
        group_configs = [
            {
                'name': 'Admin',
                'permissions': ['view', 'add', 'change', 'delete'],
                'models': ['warehouse', 'product', 'stock', 'customer', 'order', 'orderitem', 'user', 'organization']
            },
            {
                'name': 'Manager',
                'permissions': ['view', 'add', 'change', 'delete'],
                'models': ['warehouse', 'product', 'stock', 'customer', 'order', 'orderitem']
            },
            {
                'name': 'Inventory Manager',
                'permissions': ['view', 'add', 'change'],
                'models': ['warehouse', 'product', 'stock']
            },
            {
                'name': 'Sales Manager',
                'permissions': ['view', 'add', 'change'],
                'models': ['customer', 'order', 'orderitem']
            },
            {
                'name': 'Staff',
                'permissions': ['view', 'add'],
                'models': ['customer', 'order', 'orderitem', 'product', 'stock']
            },
        ]
        
        for config in group_configs:
            group, created = Group.objects.get_or_create(name=config['name'])
            
            if created:
                # Add permissions to group
                for model_name in config['models']:
                    for perm_type in config['permissions']:
                        try:
                            permission = Permission.objects.get(
                                codename=f'{perm_type}_{model_name}'
                            )
                            group.permissions.add(permission)
                        except Permission.DoesNotExist:
                            pass
                
                self.stdout.write(f'  ✓ Created group: {config["name"]}')
            else:
                self.stdout.write(f'  • Group exists: {config["name"]}')
            
            groups[config['name']] = group
        
        return groups
    
    def create_warehouses(self, organizations):
        """Create warehouses for each organization"""
        warehouses = {}
        
        warehouse_data = {
            'ethnic-world': [
                {'name': 'Ethnic World Conegliano', 'location': 'Via Zanella 130, 31015 Conegliano TV, Italy'},
                {'name': 'Ethnic World Vicenza', 'location': 'Viale Milano 37, 36100 Vicenza VI, Italy'},
                {'name': 'Ethnic World Padova', 'location': 'Via Venezia 45, 35131 Padova PD, Italy'},
            ],
            'african-heritage': [
                {'name': 'African Heritage Milano', 'location': 'Corso Buenos Aires 123, Milano, Italy'},
                {'name': 'African Heritage Roma', 'location': 'Via Nazionale 100, Roma, Italy'},
            ],
            'demo-company': [
                {'name': 'Demo Milano Central', 'location': 'Via Torino 45, Milano, Italy'},
                {'name': 'Demo Roma Distribution', 'location': 'Via Nazionale 100, Roma, Italy'},
            ]
        }
        
        for org_slug, wh_list in warehouse_data.items():
            warehouses[org_slug] = []
            org = organizations[org_slug]
            
            for data in wh_list:
                warehouse, created = Warehouse.objects.get_or_create(
                    name=data['name'],
                    organization=org,
                    defaults={'location': data['location'], 'is_active': True}
                )
                warehouses[org_slug].append(warehouse)
                
                if created:
                    self.stdout.write(f'  ✓ Created: {data["name"]} → {org.name}')
                else:
                    self.stdout.write(f'  • Exists: {data["name"]}')
        
        return warehouses
    
    def create_users(self, organizations, warehouses, groups):
        """Create users with organization assignments"""
        users = {}
        
        user_data = [
            # Superuser (no organization)
            {
                'username': 'superadmin',
                'email': 'superadmin@taalumaerp.com',
                'password': 'admin123',
                'first_name': 'Super',
                'last_name': 'Admin',
                'organization': None,
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'warehouse': None,
                'groups': []
            },
            
            # Ethnic World Users
            {
                'username': 'admin.ethnicworld',
                'email': 'admin@ethnicworld.it',
                'password': 'admin123',
                'first_name': 'Mario',
                'last_name': 'Rossi',
                'organization': 'ethnic-world',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': None,
                'groups': ['Admin']
            },
            {
                'username': 'manager.ethnicworld',
                'email': 'manager@ethnicworld.it',
                'password': 'manager123',
                'first_name': 'Luigi',
                'last_name': 'Bianchi',
                'organization': 'ethnic-world',
                'role': 'manager',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': None,
                'groups': ['Manager']
            },
            {
                'username': 'staff.conegliano',
                'email': 'staff.conegliano@ethnicworld.it',
                'password': 'staff123',
                'first_name': 'Antonio',
                'last_name': 'Ferrari',
                'organization': 'ethnic-world',
                'role': 'staff',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': ('ethnic-world', 0),  # First warehouse
                'groups': ['Staff']
            },
            
            # African Heritage Users
            {
                'username': 'admin.african',
                'email': 'admin@africanheritage.com',
                'password': 'admin123',
                'first_name': 'Giuseppe',
                'last_name': 'Verdi',
                'organization': 'african-heritage',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': None,
                'groups': ['Admin']
            },
            {
                'username': 'staff.african',
                'email': 'staff@africanheritage.com',
                'password': 'staff123',
                'first_name': 'Francesco',
                'last_name': 'Ricci',
                'organization': 'african-heritage',
                'role': 'staff',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': ('african-heritage', 0),
                'groups': ['Staff']
            },
            
            # Demo Company Users
            {
                'username': 'demo_admin',
                'email': 'admin@demo.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'organization': 'demo-company',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': None,
                'groups': ['Admin']
            },
            {
                'username': 'demo_manager',
                'email': 'manager@demo.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'Manager',
                'organization': 'demo-company',
                'role': 'manager',
                'is_staff': True,
                'is_superuser': False,
                'warehouse': None,
                'groups': ['Manager']
            },
        ]
        
        for data in user_data:
            # Get organization
            org = organizations.get(data['organization']) if data['organization'] else None
            
            # Get warehouse
            warehouse = None
            if data['warehouse']:
                org_slug, wh_index = data['warehouse']
                warehouse = warehouses[org_slug][wh_index]
            
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'organization': org,
                    'role': data['role'],
                    'is_staff': data['is_staff'],
                    'is_superuser': data['is_superuser'],
                    'assigned_warehouse': warehouse
                }
            )
            
            if created:
                user.set_password(data['password'])
                
                # Add to groups
                for group_name in data['groups']:
                    if group_name in groups:
                        user.groups.add(groups[group_name])
                
                user.save()
                
                org_name = org.name if org else 'Platform Admin'
                wh_name = warehouse.name if warehouse else 'All Locations'
                self.stdout.write(
                    f'  ✓ {data["username"]} → {org_name} @ {wh_name}'
                )
            else:
                self.stdout.write(f'  • Exists: {data["username"]}')
            
            users[data['username']] = user
        
        return users
    
    def create_products(self, count, users, organizations):
        """Create products for each organization"""
        products = {}
        
        product_categories = {
            'Textiles': ['Sari Silk', 'Batik Fabric', 'Kente Cloth', 'Ikat Textile', 'Mud Cloth'],
            'Spices': ['Turmeric', 'Cardamom', 'Saffron', 'Curry Blend', 'Garam Masala'],
            'Cosmetics': ['Argan Oil', 'Shea Butter', 'Henna Powder', 'Black Soap', 'Rose Water'],
            'Crafts': ['Wooden Mask', 'Clay Pottery', 'Beaded Jewelry', 'Brass Statue', 'Woven Basket'],
            'Food': ['Basmati Rice', 'Chickpea Flour', 'Coconut Oil', 'Palm Oil', 'Tamarind Paste']
        }
        
        for org_slug, org in organizations.items():
            products[org_slug] = []
            admin_user = users.get(f'admin.{org_slug.replace("-", "")}') or users.get(f'{org_slug.replace("-", "_")}_admin')
            
            if not admin_user:
                continue
            
            idx = 1
            for category, items in product_categories.items():
                for item_name in items:
                    if idx > count // len(organizations):
                        break
                    
                    sku = f'{org_slug[:3].upper()}-{category[:3].upper()}-{idx:03d}'
                    cost = Decimal(str(round(random.uniform(3, 40), 2)))
                    selling = Decimal(str(round(float(cost) * random.uniform(1.5, 2.5), 2)))
                    
                    product, created = Product.objects.get_or_create(
                        sku=sku,
                        defaults={
                            'name': item_name,
                            'category': category,
                            'cost_price': cost,
                            'selling_price': selling,
                            'description': f'Authentic {item_name.lower()} imported from origin',
                            'is_active': True,
                            'created_by': admin_user,
                        }
                    )
                    
                    products[org_slug].append(product)
                    
                    if created:
                        self.stdout.write(f'  ✓ {sku}: {item_name} → {org.name}')
                    
                    idx += 1
        
        return products
    
    def create_stock(self, products, warehouses, users):
        """Create stock for each organization"""
        stock_count = 0
        
        for org_slug, product_list in products.items():
            wh_list = warehouses.get(org_slug, [])
            
            for product in product_list:
                for warehouse in wh_list:
                    quantity = random.randint(20, 300)
                    reorder = random.randint(10, 30)
                    
                    stock, created = Stock.objects.get_or_create(
                        product=product,
                        warehouse=warehouse,
                        defaults={
                            'quantity': quantity,
                            'reorder_level': reorder,
                            'created_by': product.created_by,
                        }
                    )
                    
                    if created:
                        stock_count += 1
        
        self.stdout.write(f'  ✓ Created {stock_count} stock records')
    
    def create_customers(self, count, users, organizations):
        """Create customers for each organization"""
        customers = {}
        
        italian_names = [
            ('Giovanni', 'Romano'), ('Maria', 'Rizzo'), ('Giuseppe', 'Fontana'),
            ('Anna', 'Marino'), ('Francesco', 'Greco'), ('Laura', 'Bruno'),
            ('Alessandro', 'Galli'), ('Sofia', 'Conti'), ('Matteo', 'De Luca'),
        ]
        
        for org_slug, org in organizations.items():
            customers[org_slug] = []
            admin_user = users.get(f'admin.{org_slug.replace("-", "")}') or users.get(f'{org_slug.replace("-", "_")}_admin')
            
            if not admin_user:
                continue
            
            for i in range(count // len(organizations)):
                first_name, last_name = random.choice(italian_names)
                
                customer, created = Customer.objects.get_or_create(
                    email=f'{first_name.lower()}.{last_name.lower()}.{org_slug}.{i+1}@example.it',
                    defaults={
                        'name': f'{first_name} {last_name}',
                        'phone': f'+39 3{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}',
                        'address': f'Via Roma {random.randint(1,150)}, Italia',
                        'is_active': True,
                        'created_by': admin_user,
                    }
                )
                
                customers[org_slug].append(customer)
                
                if created and i % 3 == 0:
                    self.stdout.write(f'  ✓ {customer.name} → {org.name}')
        
        return customers
    
    def create_orders(self, count, customers, products, warehouses, users):
        """Create orders for each organization"""
        statuses = ['pending', 'confirmed', 'shipped', 'delivered']
        
        for org_slug in customers.keys():
            org_customers = customers[org_slug]
            org_products = products.get(org_slug, [])
            org_warehouses = warehouses.get(org_slug, [])
            
            if not org_customers or not org_products or not org_warehouses:
                continue
            
            for i in range(count // len(customers)):
                customer = random.choice(org_customers)
                warehouse = random.choice(org_warehouses)
                status = random.choice(statuses)
                
                order = Order.objects.create(
                    customer=customer,
                    warehouse=warehouse,
                    status=status,
                    created_by=customer.created_by,
                )
                
                # Add items
                num_items = random.randint(1, 3)
                for _ in range(num_items):
                    product = random.choice(org_products)
                    quantity = random.randint(1, 5)
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.selling_price,
                    )
                
                order.calculate_total()
                
                if status in ['confirmed', 'shipped', 'delivered']:
                    try:
                        order.deduct_stock()
                    except:
                        pass
        
        self.stdout.write(f'  ✓ Created orders across all organizations')
    
    def print_summary(self, organizations, users, warehouses):
        """Print summary"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 TEST DATA SUMMARY'))
        self.stdout.write('=' * 70)
        
        self.stdout.write('\n🏢 ORGANIZATIONS:')
        for org_slug, org in organizations.items():
            wh_count = len(warehouses.get(org_slug, []))
            self.stdout.write(f'  • {org.name} ({wh_count} warehouses)')
        
        self.stdout.write('\n👥 KEY USER ACCOUNTS:')
        self.stdout.write(f'  • superadmin / admin123 (Platform Admin)')
        self.stdout.write(f'  • admin.ethnicworld / admin123 (Ethnic World)')
        self.stdout.write(f'  • admin.african / admin123 (African Heritage)')
        self.stdout.write(f'  • demo_admin / demo123 (Demo Company)')
        
        self.stdout.write('\n📦 DATABASE STATS:')
        self.stdout.write(f'  • Organizations: {Organization.objects.count()}')
        self.stdout.write(f'  • Warehouses: {Warehouse.objects.count()}')
        self.stdout.write(f'  • Products: {Product.objects.count()}')
        self.stdout.write(f'  • Stock Records: {Stock.objects.count()}')
        self.stdout.write(f'  • Customers: {Customer.objects.count()}')
        self.stdout.write(f'  • Orders: {Order.objects.count()}')
        
        self.stdout.write('\n🌐 ADMIN URL:')
        self.stdout.write('  https://taaluma-erp.up.railway.app/admin/')
