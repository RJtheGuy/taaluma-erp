# TAALUMA ERP - API DOCUMENTATION

## 🔐 Security Features Implemented

### 1. Authentication
- **JWT (JSON Web Tokens)** for stateless auth
- **Session Authentication** for browser-based access
- Token refresh mechanism (7-day refresh, 1-hour access)
- Password validation (Django's built-in validators)

### 2. Authorization
- **Role-Based Access Control (RBAC)**
  - `admin`: Full access
  - `manager`: Management operations
  - `inventory_manager`: Inventory only
  - `sales_manager`: Sales only
  - `staff`: Basic sales operations

### 3. Rate Limiting
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour

### 4. Data Validation
- **Field-level validation** on all serializers
- **Business logic validation** (e.g., selling price > cost price)
- **Unique constraints** (SKU, product+warehouse stock)
- **Negative value prevention**

### 5. User Tracking
- All creates/updates tracked by user
- Audit trail via `created_by` and `updated_by`

---

## 📡 API Endpoints

### Authentication

#### Register User
```http
POST /api/users/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+39 123 456 7890",
  "role": "staff"
}
```

#### Get JWT Token
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

#### Get Current User
```http
GET /api/users/me/
Authorization: Bearer <access_token>
```

#### Change Password
```http
POST /api/users/change_password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```

---

### Inventory Management

#### List Warehouses
```http
GET /api/warehouses/
Authorization: Bearer <access_token>
```

#### Create Warehouse
```http
POST /api/warehouses/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Main Warehouse",
  "location": "Treviso, Italy",
  "is_active": true
}
```

#### Get Warehouse Stock Levels
```http
GET /api/warehouses/{id}/stock_levels/
Authorization: Bearer <access_token>
```

#### List Products
```http
GET /api/products/
Authorization: Bearer <access_token>

# With filters
GET /api/products/?category=Textiles&search=wax
```

#### Create Product
```http
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "African Wax Fabric",
  "sku": "WAX-001",
  "category": "Textiles",
  "cost_price": "5.00",
  "selling_price": "15.00",
  "description": "Traditional African print fabric",
  "is_active": true
}
```

#### Get Low Stock Products
```http
GET /api/products/low_stock/
Authorization: Bearer <access_token>
```

#### Get Product Stock Summary
```http
GET /api/products/{id}/stock_summary/
Authorization: Bearer <access_token>
```

#### List Stock
```http
GET /api/stocks/
Authorization: Bearer <access_token>

# Filter by warehouse
GET /api/stocks/?warehouse={warehouse_id}
```

#### Create Stock Entry
```http
POST /api/stocks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product": "uuid-here",
  "warehouse": "uuid-here",
  "quantity": 100,
  "reorder_level": 10
}
```

#### Adjust Stock Quantity
```http
POST /api/stocks/{id}/adjust_quantity/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "adjustment": 50  // Positive to add, negative to subtract
}
```

---

### Sales Management

#### List Customers
```http
GET /api/customers/
Authorization: Bearer <access_token>
```

#### Create Customer
```http
POST /api/customers/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Ethnic World Conegliano",
  "email": "info@ethnicworld.it",
  "phone": "+39 123 456 7890",
  "address": "Viale Venezia, 87, 31015 Conegliano",
  "is_active": true
}
```

#### Get Customer Orders
```http
GET /api/customers/{id}/orders/
Authorization: Bearer <access_token>
```

#### List Orders
```http
GET /api/orders/
Authorization: Bearer <access_token>

# Filter by status
GET /api/orders/?status=pending

# Filter by customer
GET /api/orders/?customer={customer_id}
```

#### Create Order
```http
POST /api/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "customer": "customer-uuid",
  "status": "pending",
  "notes": "Rush delivery",
  "items": [
    {
      "product": "product-uuid",
      "quantity": 10,
      "price": "15.00"
    },
    {
      "product": "another-product-uuid",
      "quantity": 5,
      "price": "25.00"
    }
  ]
}

// Note: Total is auto-calculated
// Stock is auto-deducted when status = 'confirmed'
```

#### Cancel Order
```http
POST /api/orders/{id}/cancel/
Authorization: Bearer <access_token>
```

#### Get Order Statistics
```http
GET /api/orders/stats/
Authorization: Bearer <access_token>

Response:
{
  "total": 150,
  "pending": 20,
  "confirmed": 80,
  "shipped": 30,
  "delivered": 15,
  "cancelled": 5,
  "total_revenue": "125000.00"
}
```

---

### Analytics

#### List Predictions
```http
GET /api/predictions/
Authorization: Bearer <access_token>

# Filter by product
GET /api/predictions/?product={product_id}

# Filter by date
GET /api/predictions/?date=2025-01-15
```

#### List Sales Metrics
```http
GET /api/metrics/
Authorization: Bearer <access_token>

# Filter by type
GET /api/metrics/?metric_type=daily
```

#### Get Last 30 Days Metrics
```http
GET /api/metrics/last_30_days/
Authorization: Bearer <access_token>
```

---

## 🛡️ Permission Matrix

| Role | Inventory | Sales | Analytics | User Management |
|------|-----------|-------|-----------|----------------|
| admin | ✅ Full | ✅ Full | ✅ View | ✅ Full |
| manager | ✅ Full | ✅ Full | ✅ View | ❌ None |
| inventory_manager | ✅ Full | ❌ None | ❌ None | ❌ None |
| sales_manager | ❌ None | ✅ Full | ❌ None | ❌ None |
| staff | ❌ Read | ✅ Create/Read | ❌ None | ❌ None |

---

## 📝 Validation Rules

### Products
- SKU: Minimum 3 characters, unique, auto-uppercase
- Name: Minimum 2 characters
- Prices: Must be >= 0
- Selling price should not be less than cost price (warning)

### Stock
- Quantity: Cannot be negative
- Reorder level: Cannot be negative
- Product + Warehouse: Must be unique combination

### Orders
- Must have at least one item
- Item quantity: Must be > 0
- Item price: Cannot be negative
- Total: Auto-calculated from items
- Stock: Auto-deducted when status changes to 'confirmed'

### Customers
- Name: Minimum 2 characters
- Email: Valid email format, auto-lowercase

---

## 🔄 Business Logic

### Automatic Stock Deduction
When an order status changes to 'confirmed':
1. System finds available stock in any warehouse
2. Deducts ordered quantity from stock
3. If insufficient stock, order remains but stock stays unchanged

### Order Total Calculation
- Automatically calculated from order items
- Formula: `sum(item.quantity * item.price)`
- Updates on order create/update

### User Tracking
- All creates record `created_by`
- All updates record `updated_by`
- Provides audit trail

---

## 🚀 Testing with cURL

### Get Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Create Product
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "sku": "TEST-001",
    "category": "Test",
    "cost_price": "10.00",
    "selling_price": "20.00"
  }'
```

### List Products
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## ⚠️ Important Notes

1. **JWT Tokens expire after 1 hour** - use refresh endpoint
2. **Rate limits apply** - 1000 req/hour for authenticated users
3. **All prices are Decimal** - use strings in JSON ("10.00")
4. **UUIDs are used** - not integer IDs
5. **Stock deduction is automatic** - when order confirmed
6. **Permissions are enforced** - respect role-based access

---

## 🔧 Next Steps for Production

1. Enable HTTPS only
2. Set up CORS properly
3. Add API documentation UI (Swagger/ReDoc)
4. Implement request logging
5. Add comprehensive tests
6. Set up monitoring
7. Configure PostgreSQL
8. Add backup strategy

---

## 📚 Additional Resources

- JWT: https://jwt.io/
- DRF: https://www.django-rest-framework.org/
- Postman Collection: [Create based on these endpoints]
