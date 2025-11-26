# apps/inventory/views.py
# Add this to your existing views.py or create if it doesn't exist

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Warehouse, Stock
import csv
import io
from decimal import Decimal


@staff_member_required
def bulk_upload_products(request):
    """Bulk upload products via CSV"""
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file to upload.')
            return redirect('admin:inventory_product_changelist')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV file (.csv extension)')
            return redirect('admin:inventory_product_changelist')
        
        try:
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    try:
                        # Extract data from CSV
                        name = row.get('name', '').strip()
                        sku = row.get('sku', '').strip()
                        category = row.get('category', '').strip()
                        cost_price = row.get('cost_price', '0').strip()
                        selling_price = row.get('selling_price', '0').strip()
                        description = row.get('description', '').strip()
                        
                        # Validate required fields
                        if not name or not sku:
                            errors.append(f"Row {row_num}: Missing name or SKU")
                            continue
                        
                        # Convert prices
                        try:
                            cost_price = Decimal(cost_price) if cost_price else Decimal('0')
                            selling_price = Decimal(selling_price) if selling_price else Decimal('0')
                        except:
                            errors.append(f"Row {row_num}: Invalid price format for {name}")
                            continue
                        
                        # Create or update product
                        product, created = Product.objects.update_or_create(
                            sku=sku,
                            defaults={
                                'name': name,
                                'category': category,
                                'cost_price': cost_price,
                                'selling_price': selling_price,
                                'description': description,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Show results
            if created_count > 0:
                messages.success(request, f'✅ Successfully created {created_count} products')
            
            if updated_count > 0:
                messages.success(request, f'✅ Successfully updated {updated_count} products')
            
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... and {len(errors) - 10} more errors')
            
            return redirect('admin:inventory_product_changelist')
        
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
            return redirect('admin:inventory_product_changelist')
    
    # GET request - show upload form
    return render(request, 'admin/inventory/bulk_upload_products.html')


@staff_member_required
def bulk_upload_stock(request):
    """Bulk upload stock records via CSV"""
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file to upload.')
            return redirect('admin:inventory_stock_changelist')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV file (.csv extension)')
            return redirect('admin:inventory_stock_changelist')
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    try:
                        sku = row.get('sku', '').strip()
                        warehouse_name = row.get('warehouse', '').strip()
                        quantity = row.get('quantity', '0').strip()
                        reorder_level = row.get('reorder_level', '10').strip()
                        
                        # Validate
                        if not sku or not warehouse_name:
                            errors.append(f"Row {row_num}: Missing SKU or warehouse")
                            continue
                        
                        # Find product
                        try:
                            product = Product.objects.get(sku=sku)
                        except Product.DoesNotExist:
                            errors.append(f"Row {row_num}: Product with SKU {sku} not found")
                            continue
                        
                        # Find warehouse
                        try:
                            warehouse = Warehouse.objects.get(name__icontains=warehouse_name)
                        except Warehouse.DoesNotExist:
                            errors.append(f"Row {row_num}: Warehouse {warehouse_name} not found")
                            continue
                        
                        # Convert numbers
                        try:
                            quantity = int(quantity)
                            reorder_level = int(reorder_level)
                        except:
                            errors.append(f"Row {row_num}: Invalid quantity format")
                            continue
                        
                        # Create or update stock
                        stock, created = Stock.objects.update_or_create(
                            product=product,
                            warehouse=warehouse,
                            defaults={
                                'quantity': quantity,
                                'reorder_level': reorder_level,
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            if created_count > 0:
                messages.success(request, f'✅ Successfully created {created_count} stock records')
            
            if updated_count > 0:
                messages.success(request, f'✅ Successfully updated {updated_count} stock records')
            
            if errors:
                for error in errors[:10]:
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... and {len(errors) - 10} more errors')
            
            return redirect('admin:inventory_stock_changelist')
        
        except Exception as e:
            messages.error(request, f'Error processing CSV: {str(e)}')
            return redirect('admin:inventory_stock_changelist')
    
    return render(request, 'admin/inventory/bulk_upload_stock.html')
