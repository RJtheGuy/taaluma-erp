import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR('Error: ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD must be set')
            )
            return
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Superuser {username} created successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Superuser {username} already exists.')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
            raise
