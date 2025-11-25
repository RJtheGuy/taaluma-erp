# accounts/migrations/0002_user_assigned_warehouse.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='assigned_warehouse',
            field=models.ForeignKey(
                blank=True,
                help_text='Assign user to specific warehouse for location-based access. Leave empty for full access.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_users',
                to='inventory.warehouse',
                verbose_name='Assigned Warehouse'
            ),
        ),
    ]
