from celery import shared_task
from apps.sales.models import OrderItem
from apps.analytics.models import Prediction, SalesMetric
from django.db.models import Sum, Count
from datetime import date


@shared_task
def generate_sales_prediction(product_id):
    """
    Generate ML-based sales prediction for a product
    TODO: Integrate ML model (Prophet/LSTM)
    """
    # Placeholder - will add ML logic later
    pass


@shared_task
def calculate_daily_metrics():
    """Calculate daily sales metrics"""
    today = date.today()
    
    # Aggregate today's sales
    orders = OrderItem.objects.filter(created_at__date=today)
    total_sales = orders.aggregate(total=Sum('subtotal'))['total'] or 0
    total_orders = orders.values('order').distinct().count()
    
    SalesMetric.objects.update_or_create(
        date=today,
        metric_type='daily',
        defaults={
            'total_sales': total_sales,
            'total_orders': total_orders
        }
    )
    
    return f"Metrics calculated for {today}"


@shared_task
def check_low_stock_alerts():
    """Check for low stock and send alerts"""
    from apps.inventory.models import Stock
    
    low_stocks = Stock.objects.filter(quantity__lte=models.F('reorder_level'))
    
    # TODO: Send email/SMS alerts
    return f"Found {low_stocks.count()} low stock items"
