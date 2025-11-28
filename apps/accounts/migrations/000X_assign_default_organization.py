# apps/accounts/migrations/000X_assign_default_organization.py
# Run this AFTER creating the Organization model
from django.db import migrations


def assign_default_organization(apps, schema_editor):
    """
    Create a default organization and assign all existing data to it.
    This is for backward compatibility with existing Ethnic World data.
    """
    Organization = apps.get_model('accounts', 'Organization')
    User = apps.get_model('accounts', 'User')
    Warehouse = apps.get_model('inventory', 'Warehouse')
    
    # Create default organization for Ethnic World
    ethnic_world, created = Organization.objects.get_or_create(
        slug='ethnic-world',
        defaults={
            'name': 'Ethnic World',
            'subscription_status': 'active',
            'monthly_fee': 300.00,
            'contact_email': 'info@ethnicworld.it',
        }
    )
    
    if created:
        print(f"✅ Created organization: {ethnic_world.name}")
    
    # Assign all existing users to Ethnic World
    users_updated = User.objects.filter(organization__isnull=True).update(
        organization=ethnic_world
    )
    print(f"✅ Assigned {users_updated} users to {ethnic_world.name}")
    
    # Assign all existing warehouses to Ethnic World
    warehouses_updated = Warehouse.objects.filter(organization__isnull=True).update(
        organization=ethnic_world
    )
    print(f"✅ Assigned {warehouses_updated} warehouses to {ethnic_world.name}")


def reverse_assignment(apps, schema_editor):
    """Reverse the migration if needed"""
    Organization = apps.get_model('accounts', 'Organization')
    Organization.objects.filter(slug='ethnic-world').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '000X_add_organization'),  # Update to your migration number
        ('inventory', '000X_add_organization_to_warehouse'),  # Update to your migration number
    ]

    operations = [
        migrations.RunPython(assign_default_organization, reverse_assignment),
    ]
