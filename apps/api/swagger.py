from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Taaluma ERP API",
        default_version='v1',
        description="""
# Taaluma ERP - API Documentation

Enterprise Resource Planning system for African diaspora import/export businesses.

## Features
- **Inventory Management**: Products, warehouses, stock tracking
- **Sales Management**: Customers, orders, order items
- **Analytics**: Sales metrics, ML predictions
- **User Management**: JWT authentication, role-based access

## Authentication
This API uses JWT (JSON Web Tokens) for authentication.

To authenticate:
1. POST to `/api/auth/token/` with username and password
2. Receive access and refresh tokens
3. Include access token in header: `Authorization: Bearer <token>`
4. Refresh token before expiry using `/api/auth/token/refresh/`

## Rate Limiting
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour

## Pagination
- Default page size: 20 items
- Max page size: 100 items
- Use `?page=2` for pagination
- Use `?page_size=50` to customize

## Filtering & Search
Most list endpoints support:
- `?search=keyword` - Search across multiple fields
- `?ordering=field_name` - Order results
- `?field_name=value` - Filter by specific field

## Support
Contact: your-email@example.com
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@taalumaerp.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
