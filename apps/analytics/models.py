from django.db import models
from apps.core.models import BaseModel


class Prediction(BaseModel):
    """ML prediction results storage"""
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE, related_name="predictions")
    date = models.DateField()
    predicted_quantity = models.IntegerField()
    confidence_score = models.FloatField(null=True, blank=True)
    model_version = models.CharField(max_length=50)

    class Meta:
        db_table = "predictions"
        ordering = ["-date"]
        
    def __str__(self):
        return f"Prediction for {self.product.name} on {self.date}"


class SalesMetric(BaseModel):
    """Aggregated sales metrics for dashboards"""
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    metric_type = models.CharField(max_length=50)  # daily, weekly, monthly

    class Meta:
        db_table = "sales_metrics"
        unique_together = ["date", "metric_type"]
        ordering = ["-date"]
