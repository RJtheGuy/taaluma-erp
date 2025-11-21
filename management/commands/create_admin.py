import os
import django
import sys

# Aggiungi il percorso corrente
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings'))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('ADMIN_USERNAME')
email = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASSWORD')

if not all([username, email, password]):
    print("Error: ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD must be set")
    sys.exit(1)

try:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser {username} created successfully!')
    else:
        print(f'Superuser {username} already exists.')
except Exception as e:
    print(f'Error creating superuser: {e}')
    sys.exit(1)
