# apps/sales/views.py
# Add this to create Quick Sale Entry functionality

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Customer
from apps.inventory.models import Product, Warehouse, Stock
from decimal import Decimal
import json


def quick_sale_entry(request, warehouse_code):
    """
    Quick sale entry form - NO LOGIN REQUIRED
    Access via: /quick-sale/<warehouse-code>/
    
    Each warehouse gets unique URL with secret code
    Example: /quick-sale/PADOVA-X7K9M2/
    """
    
    # Validate warehouse code
    try:
        # Extract warehouse name from code (format: LOCATION-SECRET)
        warehouse_name = warehouse_code.split('-')[0]
        warehouse = Warehouse.objects.get(name__icontains=warehouse_name)
    except (Warehouse.DoesNotExist, IndexError):
        return render(request, 'sales/quick_sale_error.html', {
            'error': 'Invalid warehouse code. Contact your manager.'
        })
    
    # Get products for this warehouse (products with stock)
    products = Product.objects.filter(
        stocks__warehouse=warehouse,
        is_active=True
    ).distinct().order_by('name')
    
    # Get recent walk-in customer or create default
    walk_in_customer, _ = Customer.objects.get_or_create(
        email='walkin@store.local',
        defaults={
            'name': 'Walk-in Customer',
            'phone': '',
            'address': ''
        }
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                customer_name = request.POST.get('customer_name', 'Walk-in Customer')
                customer_phone = request.POST.get('customer_phone', '')
                
                # Create or get customer
                if customer_phone:
                    customer, _ = Customer.objects.get_or_create(
                        phone=customer_phone,
                        defaults={'name': customer_name}
                    )
                else:
                    customer = walk_in_customer
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    warehouse=warehouse,
                    status='confirmed',  # Auto-confirm quick sales
                    notes=f'Quick sale entry at {warehouse.name}'
                )
                
                # Add order items
                items_added = 0
                total = Decimal('0.00')
                
                # Get all product/quantity pairs from POST data
                for key in request.POST:
                    if key.startswith('quantity_'):
                        product_id = key.replace('quantity_', '')
                        quantity = request.POST.get(key)
                        
                        if quantity and int(quantity) > 0:
                            product = Product.objects.get(id=product_id)
                            quantity = int(quantity)
                            
                            # Check stock availability
                            try:
                                stock = Stock.objects.get(
                                    product=product,
                                    warehouse=warehouse
                                )
                                
                                if stock.quantity < quantity:
                                    messages.warning(
                                        request,
                                        f'⚠️ Only {stock.quantity} units of {product.name} available. Order not created.'
                                    )
                                    order.delete()
                                    return redirect('quick_sale_entry', warehouse_code=warehouse_code)
                            
                            except Stock.DoesNotExist:
                                messages.error(
                                    request,
                                    f'❌ {product.name} not available at this location. Order not created.'
                                )
                                order.delete()
                                return redirect('quick_sale_entry', warehouse_code=warehouse_code)
                            
                            # Create order item
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                quantity=quantity,
                                price=product.selling_price,
                                subtotal=quantity * product.selling_price
                            )
                            
                            items_added += 1
                            total += quantity * product.selling_price
                
                if items_added == 0:
                    order.delete()
                    messages.warning(request, '⚠️ No items added. Please select at least one product.')
                    return redirect('quick_sale_entry', warehouse_code=warehouse_code)
                
                # Calculate total and deduct stock
                order.calculate_total()
                order.deduct_stock()
                
                messages.success(
                    request,
                    f'✅ Sale recorded! Order #{str(order.id)[:8]} - Total: €{total:.2f} - {items_added} items'
                )
                
                return redirect('quick_sale_entry', warehouse_code=warehouse_code)
        
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('quick_sale_entry', warehouse_code=warehouse_code)
    
    # GET request - show form
    context = {
        'warehouse': warehouse,
        'products': products,
        'warehouse_code': warehouse_code,
    }
    
    return render(request, 'sales/quick_sale_entry.html', context)


@csrf_exempt
def quick_sale_api(request, warehouse_code):
    """
    API endpoint for mobile/tablet apps
    POST JSON data to create sale
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate warehouse
        warehouse_name = warehouse_code.split('-')[0]
        warehouse = Warehouse.objects.get(name__icontains=warehouse_name)
        
        # Get customer
        walk_in_customer, _ = Customer.objects.get_or_create(
            email='walkin@store.local',
            defaults={'name': 'Walk-in Customer'}
        )
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                customer=walk_in_customer,
                warehouse=warehouse,
                status='confirmed'
            )
            
            # Add items
            for item in data.get('items', []):
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.selling_price,
                    subtotal=quantity * product.selling_price
                )
            
            order.calculate_total()
            order.deduct_stock()
        
        return JsonResponse({
            'success': True,
            'order_id': str(order.id),
            'total': float(order.total)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
