# QUICK START GUIDE - Taaluma ERP

## ✅ What's Been Built

You now have a **production-ready Django ERP foundation** with:

### Core Architecture
- ✅ Django 5.2.8 project with clean app structure
- ✅ Custom User model (accounts app)
- ✅ Abstract base models (BaseModel, TrackableModel)
- ✅ Split settings (base.py, local.py)
- ✅ Celery + Redis configuration

### Database Models
- ✅ **Inventory**: Warehouse, Product, Stock
- ✅ **Sales**: Customer, Order, OrderItem  
- ✅ **Analytics**: Prediction, SalesMetric
- ✅ All migrations created and applied

### Admin Interface
- ✅ All models registered in Django admin
- ✅ Custom admin views with search/filters
- ✅ Inline editing for OrderItems

### Background Tasks
- ✅ Celery tasks structure ready
- ✅ Sales prediction placeholder
- ✅ Daily metrics calculation
- ✅ Low stock alert system

## 🚀 Getting Started

### 1. Extract and Setup
```bash
# Extract the archive
tar -xzf taaluma-erp-foundation.tar.gz
cd taaluma-erp

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Start Development
```bash
# Activate environment
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.local

# Run server
python manage.py runserver
```

Access: http://127.0.0.1:8000/admin/

### 3. Test the System
```bash
# Create test data
python manage.py shell

>>> from apps.inventory.models import Product, Warehouse, Stock
>>> from apps.sales.models import Customer, Order, OrderItem
>>> 
>>> # Create warehouse
>>> wh = Warehouse.objects.create(name="Main Warehouse", location="Treviso")
>>> 
>>> # Create product
>>> product = Product.objects.create(
...     name="African Wax Fabric",
...     sku="WAX-001",
...     category="Textiles",
...     cost_price=5.00,
...     selling_price=15.00
... )
>>> 
>>> # Create stock
>>> Stock.objects.create(product=product, warehouse=wh, quantity=100)
```

## 📋 Next Development Steps

### Immediate (Week 1-2)
1. **Build REST API**
   - Create serializers for all models
   - Build ViewSets
   - Set up routing in apps/api/

2. **Add Authentication**
   - JWT or Token authentication
   - Permission classes
   - User registration endpoint

### Short Term (Week 3-4)
3. **Business Logic**
   - Auto-deduct stock on order confirmation
   - Calculate order totals automatically
   - Email notifications for low stock

4. **Multi-currency Support**
   - Add Currency model
   - Price conversion logic
   - Exchange rate updates via API

### Medium Term (Month 2)
5. **ML Integration**
   - Sales forecasting with Prophet
   - Train on historical order data
   - Schedule daily predictions

6. **Dashboard API**
   - Sales summary endpoints
   - Inventory levels
   - Top products/customers

## 🎯 Recommended Next Action

**Build the REST API first** - This will allow you to:
- Test the models thoroughly
- Build the frontend against real endpoints
- Demonstrate the system to potential clients

Create this structure:
```
apps/api/
├── serializers.py
├── views.py
├── urls.py
└── permissions.py
```

### Example API Structure
```python
# apps/api/serializers.py
from rest_framework import serializers
from apps.inventory.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# apps/api/views.py
from rest_framework import viewsets
from apps.inventory.models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# apps/api/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = router.urls
```

## 📊 Current Project Status

| Component | Status | Priority |
|-----------|--------|----------|
| Database Models | ✅ Complete | - |
| Django Admin | ✅ Complete | - |
| Celery Setup | ✅ Complete | - |
| REST API | ⏳ Not started | HIGH |
| Authentication | ⏳ Not started | HIGH |
| Business Logic | ⏳ Not started | MEDIUM |
| ML Models | ⏳ Not started | MEDIUM |
| Frontend | ⏳ Not started | LOW |
| Docker | ⏳ Not started | LOW |

## 🔧 Useful Commands

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run Celery worker
celery -A config worker -l info

# Run tests (when you add them)
python manage.py test
```

## 📂 Project Files

```
taaluma-erp/
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── manage.py             # Django management
├── config/               # Project configuration
│   ├── settings/
│   │   ├── base.py       # Main settings
│   │   └── local.py      # Dev settings
│   ├── celery.py         # Celery config
│   └── urls.py           # URL routing
└── apps/                 # Application modules
    ├── core/             # Base models
    ├── accounts/         # User management
    ├── inventory/        # Products & stock
    ├── sales/            # Orders & customers
    ├── analytics/        # ML & metrics
    └── api/              # REST API (build this next)
```

## 🎓 Learning Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Celery Docs: https://docs.celeryproject.org/

## ⚡ Performance Tips

1. Use select_related() for foreign keys
2. Use prefetch_related() for many-to-many
3. Add database indexes on frequently queried fields
4. Cache API responses with Redis
5. Use Celery for long-running tasks

## 🔐 Security Checklist (Before Production)

- [ ] Change SECRET_KEY in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables (.env file)
- [ ] Enable HTTPS only
- [ ] Set up CORS properly
- [ ] Add rate limiting
- [ ] Regular backups

## 📞 Need Help?

This is your foundation. Build on it step by step:
1. API layer
2. Business logic
3. Frontend
4. ML integration
5. Production deployment

Each step can be tackled independently!
