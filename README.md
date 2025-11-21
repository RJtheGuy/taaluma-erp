# Taaluma ERP - Intelligence for African Trade

Django-based ERP system with data science capabilities for Africa-Europe import/export businesses.

## Project Structure

```
taaluma-erp/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── celery.py          # Celery configuration
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py         # Base settings
│       └── local.py        # Local development settings
└── apps/
    ├── core/               # Abstract base models
    ├── accounts/           # User management
    ├── inventory/          # Products, warehouses, stock
    ├── sales/              # Orders, customers
    ├── analytics/          # ML predictions, metrics
    └── api/                # REST API (to be built)
```

## Core Features

### 1. Core Models (apps/core)
- **BaseModel**: UUID primary keys, timestamps
- **TrackableModel**: User tracking (created_by, updated_by)

### 2. Accounts (apps/accounts)
- Custom User model with phone and role
- Extended Django authentication

### 3. Inventory (apps/inventory)
- **Warehouse**: Storage locations
- **Product**: SKU, pricing, categories
- **Stock**: Quantity per warehouse with reorder levels

### 4. Sales (apps/sales)
- **Customer**: Contact management
- **Order**: Order tracking with status
- **OrderItem**: Line items with auto-calculated subtotals

### 5. Analytics (apps/analytics)
- **Prediction**: ML model results storage
- **SalesMetric**: Aggregated metrics (daily/weekly/monthly)
- Celery tasks for async processing

## Setup Instructions

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Access admin at: http://127.0.0.1:8000/admin/

### 5. Start Celery (Optional)
First, ensure Redis is running, then:
```bash
celery -A config worker -l info
```

## Database Schema

### Users Table
- id (UUID)
- username, email, password
- phone, role
- timestamps

### Products Table
- id (UUID)
- name, sku (unique)
- category
- cost_price, selling_price
- description
- is_active
- created_by, updated_by
- timestamps

### Orders Table
- id (UUID)
- customer (FK)
- total
- status (pending/confirmed/shipped/delivered/cancelled)
- notes
- created_by, updated_by
- timestamps

### Order Items Table
- id (UUID)
- order (FK)
- product (FK)
- quantity, price
- subtotal (auto-calculated)
- timestamps

## Next Steps

### Phase 1: API Development
- [ ] Create serializers for all models
- [ ] Build ViewSets with CRUD operations
- [ ] Set up API routing
- [ ] Add authentication (JWT/Token)
- [ ] API documentation (Swagger/ReDoc)

### Phase 2: Business Logic
- [ ] Inventory management signals
- [ ] Order workflow automation
- [ ] Stock level alerts
- [ ] Multi-currency support
- [ ] Supplier management

### Phase 3: Analytics & ML
- [ ] Demand forecasting (Prophet/LSTM)
- [ ] Sales trend analysis
- [ ] Customer segmentation
- [ ] Automated reporting
- [ ] Dashboard data endpoints

### Phase 4: Frontend
- [ ] Choose framework (React/Vue/HTMX)
- [ ] Dashboard design
- [ ] Inventory management UI
- [ ] Order processing UI
- [ ] Analytics visualizations

### Phase 5: Production Ready
- [ ] PostgreSQL configuration
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Environment management
- [ ] Security hardening
- [ ] Performance optimization

## Technology Stack

- **Backend**: Django 5.2.8
- **API**: Django REST Framework 3.16.1
- **Task Queue**: Celery 5.5.3
- **Cache/Broker**: Redis 7.1.0
- **Database**: SQLite (dev), PostgreSQL (production)

## Target Market

Small to medium African diaspora import/export businesses in Italy:
- Food importers (ethnic products)
- Textile traders (African fabrics)
- Multi-location retail chains
- Money transfer services

## Key Differentiators

1. **Multi-currency support** (XOF, NGN, EUR, USD)
2. **Demand forecasting** with ML
3. **Supplier performance tracking**
4. **Seasonal trend analysis**
5. **WhatsApp integration** (planned)
6. **Italian compliance** (fattura elettronica)

## Contributing

This is a commercial project. Contact the maintainer for collaboration opportunities.

## License

Proprietary - All rights reserved
