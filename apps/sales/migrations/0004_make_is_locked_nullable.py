# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_orderitem_options_and_more'),  # ← Change this to match your last migration
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='is_locked',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
