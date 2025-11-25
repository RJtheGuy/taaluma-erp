from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination with page numbers"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination for large datasets"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination for small datasets (mobile-friendly)"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """Limit/offset pagination with custom response"""
    default_limit = 20
    max_limit = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'limit': self.get_limit(self.request),
            'offset': self.get_offset(self.request),
            'results': data
        })


class TimestampCursorPagination(CursorPagination):
    """Cursor pagination ordered by timestamp (efficient for large datasets)"""
    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'
