from rest_framework.exceptions import APIException
from rest_framework import status


class InsufficientStockException(APIException):
    """Raised when trying to deduct more stock than available"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient stock for this operation.'
    default_code = 'insufficient_stock'


class InvalidOrderStatusTransition(APIException):
    """Raised when trying to make an invalid status transition"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid order status transition.'
    default_code = 'invalid_status_transition'


class DuplicateStockEntry(APIException):
    """Raised when trying to create duplicate stock entry"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Stock entry already exists for this product and warehouse.'
    default_code = 'duplicate_stock_entry'


class ProductInactive(APIException):
    """Raised when trying to use an inactive product"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Product is not active.'
    default_code = 'product_inactive'


class CustomerInactive(APIException):
    """Raised when trying to create order for inactive customer"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Customer is not active.'
    default_code = 'customer_inactive'


class BusinessRuleViolation(APIException):
    """Generic business rule violation"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Business rule violation.'
    default_code = 'business_rule_violation'
