from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_make_is_locked_nullable'),  # or whatever your last migration is
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE customers DROP COLUMN IF EXISTS organization_id CASCADE;",
            reverse_sql="",  # Can't reverse this
        ),
    ]
