#!/usr/bin/env python
"""
Create demo data for client demonstrations
Run: python create_demo_data.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.accounts.models import Organization, User
from apps.inventory.models import Warehouse, Product, Stock
from apps.sales.models import Customer, Order, OrderItem
from decimal import Decimal


def create_demo_data():
    """Create complete demo environment"""
    
    print("🚀 Creating demo data...")
    
    # 1. Create Demo Organization
    print("\n1️⃣ Creating organization...")
    demo_org, created = Organization.objects.get_or_create(
        slug='demo-company',
        defaults={
            'name': 'Demo Import/Export Ltd',
            'subscription_status': 'active',
            'monthly_fee': Decimal('300.00'),
            'contact_email': 'demo@example.com',
            'contact_phone': '+39 123 456 7890',
            'address': 'Via Demo 123, Milano, Italy',
        }
    )
    print(f"   ✅ Organization: {demo_org.name}")
    
    # 2. Create Demo Users
    print("\n2️⃣ Creating users...")
    
    # Admin user
    demo_admin, created = User.objects.get_or_create(
        username='demo_admin',
        defaults={
            'email': 'admin@demo.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'organization': demo_org,
            'role': 'admin',
            'is_staff': True,
        }
    )
    if created:
        demo_admin.set_password('demo123')
        demo_admin.save()
    print(f"   ✅ Admin: {demo_admin.username} / demo123")
    
    # Manager user
    demo_manager, created = User.objects.get_or_create(
        username='demo_manager',
        defaults={
            'email': 'manager@demo.com',
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'organization': demo_org,
            'role': 'manager',
            'is_staff': True,
        }
    )
    if created:
        demo_manager.set_password('demo123')
        demo_manager.save()
    print(f"   ✅ Manager: {demo_manager.username} / demo123")
    
    # 3. Create Warehouses
    print("\n3️⃣ Creating warehouses...")
    
    warehouses = [
        {
            'name': 'Milano Central',
            'location': 'Via Torino 45, Milano, 20123',
        },
        {
            'name': 'Roma Distribution',
            'location': 'Via Nazionale 100, Roma, 00184',
        },
        {
            'name': 'Napoli Hub',
            'location': 'Corso Umberto 250, Napoli, 80138',
        },
    ]
    
    created_warehouses = []
    for wh_data in warehouses:
        wh, created = Warehouse.objects.get_or_create(
            name=wh_data['name'],
            organization=demo_org,
            defaults={
                'location': wh_data['location'],
                'is_active': True,
                'created_by': demo_admin,
            }
        )
        created_warehouses.append(wh)
        print(f"   ✅ {wh.name}")
    
    # 4. Create Products
    print("\n4️⃣ Creating products...")
    
    products_data = [
        {'name': 'African Print Fabric - Ankara', 'sku': 'FAB-ANK-001', 'category': 'Fabrics', 'cost': 15, 'sell': 30},
        {'name': 'Kente Cloth Traditional', 'sku': 'FAB-KEN-002', 'category': 'Fabrics', 'cost': 45, 'sell': 85},
        {'name': 'Dashiki Shirt - Men', 'sku': 'CLO-DSH-003', 'category': 'Clothing', 'cost': 20, 'sell': 45},
        {'name': 'Dashiki Dress - Women', 'sku': 'CLO-DSH-004', 'category': 'Clothing', 'cost': 25, 'sell': 55},
        {'name': 'Shea Butter - Organic 500g', 'sku': 'COS-SHE-005', 'category': 'Cosmetics', 'cost': 8, 'sell': 18},
        {'name': 'Black Soap - Natural 250g', 'sku': 'COS-SOA-006', 'category': 'Cosmetics', 'cost': 5, 'sell': 12},
        {'name': 'Wooden Mask - Hand Carved', 'sku': 'ART-MAS-007', 'category': 'Art', 'cost': 30, 'sell': 75},
        {'name': 'Djembe Drum - Medium', 'sku': 'MUS-DJE-008', 'category': 'Music', 'cost': 60, 'sell': 120},
        {'name': 'Basket - Handwoven Large', 'sku': 'HOM-BAS-009', 'category': 'Home', 'cost': 12, 'sell': 28},
        {'name': 'Coffee Beans - Ethiopian 1kg', 'sku': 'FOO-COF-010', 'category': 'Food', 'cost': 10, 'sell': 22},
    ]
    
    created_products = []
    for prod_data in products_data:
        prod, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'category': prod_data['category'],
                'cost_price': Decimal(str(prod_data['cost'])),
                'selling_price': Decimal(str(prod_data['sell'])),
                'description': f"High-quality {prod_data['name'].lower()} imported from Africa",
                'is_active': True,
                'created_by': demo_admin,
            }
        )
        created_products.append(prod)
        print(f"   ✅ {prod.name}")
    
    # 5. Create Stock
    print("\n5️⃣ Creating stock records...")
    
    import random
    for warehouse in created_warehouses:
        for product in created_products:
            quantity = random.randint(20, 200)
            stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={
                    'quantity': quantity,
                    'reorder_level': 20,
                    'created_by': demo_admin,
                }
            )
            if created:
                print(f"   ✅ {product.name[:30]:30} @ {warehouse.name[:20]:20} = {quantity:3} units")
    
    # 6. Create Customers
    print("\n6️⃣ Creating customers...")
    
    customers_data = [
        {'name': 'Boutique Afrique Milano', 'email': 'info@boutiqueafrique.it', 'phone': '+39 02 1234 5678'},
        {'name': 'African Heritage Store', 'email': 'orders@africanheritage.it', 'phone': '+39 06 8765 4321'},
        {'name': 'Ethnic Fusion Roma', 'email': 'contact@ethnicfusion.it', 'phone': '+39 06 5555 1234'},
        {'name': 'Global Imports SRL', 'email': 'sales@globalimports.it', 'phone': '+39 02 9999 8888'},
        {'name': 'Arte Africana Gallery', 'email': 'info@arteafricana.it', 'phone': '+39 081 7777 6666'},
    ]
    
    created_customers = []
    for cust_data in customers_data:
        cust, created = Customer.objects.get_or_create(
            email=cust_data['email'],
            defaults={
                'name': cust_data['name'],
                'phone': cust_data['phone'],
                'address': 'Via Example 123, Italia',
                'is_active': True,
                'created_by': demo_admin,
            }
        )
        created_customers.append(cust)
        print(f"   ✅ {cust.name}")
    
    # 7. Create Sample Orders
    print("\n7️⃣ Creating sample orders...")
    
    # Pending Order
    order1, created = Order.objects.get_or_create(
        customer=created_customers[0],
        warehouse=created_warehouses[0],
        status='pending',
        defaults={
            'notes': 'Customer requested delivery next week',
            'created_by': demo_manager,
        }
    )
    if created:
        OrderItem.objects.create(
            order=order1,
            product=created_products[0],
            quantity=10,
            price=created_products[0].selling_price,
            subtotal=10 * created_products[0].selling_price,
        )
        OrderItem.objects.create(
            order=order1,
            product=created_products[2],
            quantity=5,
            price=created_products[2].selling_price,
            subtotal=5 * created_products[2].selling_price,
        )
        order1.calculate_total()
        print(f"   ✅ Pending Order: €{order1.total}")
    
    # Confirmed Order
    order2, created = Order.objects.get_or_create(
        customer=created_customers[1],
        warehouse=created_warehouses[1],
        status='confirmed',
        defaults={
            'notes': 'Rush order - priority shipping',
            'created_by': demo_manager,
        }
    )
    if created:
        OrderItem.objects.create(
            order=order2,
            product=created_products[4],
            quantity=20,
            price=created_products[4].selling_price,
            subtotal=20 * created_products[4].selling_price,
        )
        OrderItem.objects.create(
            order=order2,
            product=created_products[5],
            quantity=15,
            price=created_products[5].selling_price,
            subtotal=15 * created_products[5].selling_price,
        )
        order2.calculate_total()
        print(f"   ✅ Confirmed Order: €{order2.total}")
    
    # Delivered Order
    order3, created = Order.objects.get_or_create(
        customer=created_customers[2],
        warehouse=created_warehouses[0],
        status='delivered',
        defaults={
            'notes': 'Completed successfully',
            'created_by': demo_manager,
        }
    )
    if created:
        OrderItem.objects.create(
            order=order3,
            product=created_products[6],
            quantity=3,
            price=created_products[6].selling_price,
            subtotal=3 * created_products[6].selling_price,
        )
        OrderItem.objects.create(
            order=order3,
            product=created_products[7],
            quantity=2,
            price=created_products[7].selling_price,
            subtotal=2 * created_products[7].selling_price,
        )
        order3.calculate_total()
        print(f"   ✅ Delivered Order: €{order3.total}")
    
    print("\n" + "="*60)
    print("✅ DEMO DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   • Organization: {demo_org.name}")
    print(f"   • Users: 2 (demo_admin, demo_manager)")
    print(f"   • Warehouses: {len(created_warehouses)}")
    print(f"   • Products: {len(created_products)}")
    print(f"   • Customers: {len(created_customers)}")
    print(f"   • Orders: 3 (pending, confirmed, delivered)")
    print(f"\n🔐 Login Credentials:")
    print(f"   Admin:   demo_admin / demo123")
    print(f"   Manager: demo_manager / demo123")
    print(f"\n🌐 Access at: https://taaluma-erp.up.railway.app/admin/")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
