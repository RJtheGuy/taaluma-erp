from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='warehouse',
            field=models.ForeignKey(
                help_text='Warehouse fulfilling this order',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='inventory.warehouse'
            ),
        ),
    ]
