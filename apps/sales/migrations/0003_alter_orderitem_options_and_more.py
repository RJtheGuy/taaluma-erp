# sales/migrations/0003_alter_orderitem_options_and_more.py
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_order_warehouse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={},
        ),
    ]
