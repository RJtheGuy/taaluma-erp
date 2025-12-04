from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_orderitem_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='organization',
        ),
    ]
