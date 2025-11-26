from django.urls import path
from apps.inventory import views as inventory_views

urlpatterns = [
    path('admin/inventory/product/bulk-upload/', 
         inventory_views.bulk_upload_products, 
         name='bulk_upload_products'),
    
    path('admin/inventory/stock/bulk-upload/', 
         inventory_views.bulk_upload_stock, 
         name='bulk_upload_stock'),
]
