# apps/sales/migrations/0004_order_is_locked.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_orderitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]
