#!/bin/bash

# Taaluma ERP - Setup Script
# Run this after extracting the project

echo "🚀 Setting up Taaluma ERP..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.local

# Run migrations
echo "🗄️ Creating database..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "👤 Create admin user:"
python manage.py createsuperuser

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  export DJANGO_SETTINGS_MODULE=config.settings.local"
echo "  python manage.py runserver"
echo ""
echo "Admin panel: http://127.0.0.1:8000/admin/"
