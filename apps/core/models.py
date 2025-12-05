from django.db import models
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Abstract base model with UUID and timestamps"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrackableModel(BaseModel):
    """Abstract model with user tracking"""
    created_by = models.ForeignKey(
        "accounts.User", 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="created_%(class)s"
    )
    # updated_by = models.ForeignKey(
    #     "accounts.User", 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     related_name="updated_%(class)s"
    # )

    class Meta:
        abstract = True
