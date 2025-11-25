from rest_framework import status
from rest_framework.response import Response
from django.db import transaction


class AuditMixin:
    """Automatically set created_by and updated_by on objects"""
    
    def perform_create(self, serializer):
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()


class BulkCreateMixin:
    """Support bulk creation of objects"""
    
    def bulk_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            self.perform_bulk_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_bulk_create(self, serializer):
        serializer.save()


class SoftDeleteMixin:
    """Support soft deletes by setting is_active=False"""
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            if hasattr(instance, 'updated_by'):
                instance.updated_by = request.user
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return super().destroy(request, *args, **kwargs)


class ExportMixin:
    """Support exporting data as CSV"""
    
    def export_csv(self, request, *args, **kwargs):
        import csv
        from django.http import HttpResponse
        
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.basename}_export.csv"'
        
        writer = csv.writer(response)
        
        # Write headers (customize per model)
        if queryset.exists():
            headers = [field.name for field in queryset.model._meta.fields]
            writer.writerow(headers)
            
            # Write data
            for obj in queryset:
                row = [getattr(obj, field.name) for field in queryset.model._meta.fields]
                writer.writerow(row)
        
        return response


class CacheResponseMixin:
    """Cache API responses for better performance"""
    cache_timeout = 300  # 5 minutes default
    
    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        
        cache_key = f"{self.basename}_list_{request.GET.urlencode()}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return Response(cached_response)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout)
        
        return response
