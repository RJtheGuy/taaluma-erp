from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_orderitem_options_and_more'),
    ]

    operations = [
        # Use raw SQL to remove column if it exists
        migrations.RunSQL(
            sql="""
                DO $$ 
                BEGIN 
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='customers' 
                        AND column_name='organization_id'
                    ) THEN
                        ALTER TABLE customers DROP COLUMN organization_id CASCADE;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
