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
                help_text='Warehouse this user manages',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='inventory.warehouse'
            ),
        ),
    ]
