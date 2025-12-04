from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  
        ('sales', '0004_auto_20241204_0000'), 
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                help_text='Organization that owns this customer',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customers',
                to='accounts.organization'
            ),
        ),
    ]
