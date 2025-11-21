from django.contrib import admin
from .models import Prediction, SalesMetric


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'predicted_quantity', 'confidence_score', 'model_version']
    list_filter = ['date', 'model_version']
    search_fields = ['product__name']


@admin.register(SalesMetric)
class SalesMetricAdmin(admin.ModelAdmin):
    list_display = ['date', 'metric_type', 'total_sales', 'total_orders']
    list_filter = ['metric_type', 'date']
