from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        # Drop the original table created by 0001_initial
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS tracking_devicedata CASCADE;",
            reverse_sql="" # Recreating would be complex in reverse
        ),
        # Create partitioned table
        migrations.RunSQL(
            sql="""
            CREATE TABLE tracking_devicedata (
                id BIGSERIAL,
                device_id UUID NOT NULL REFERENCES tracking_device(id) ON DELETE CASCADE,
                timestamp TIMESTAMPTZ NOT NULL,
                latitude NUMERIC(10, 8) NOT NULL,
                longitude NUMERIC(11, 8) NOT NULL,
                speed NUMERIC(5, 2),
                fuel_level NUMERIC(5, 2),
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                PRIMARY KEY (id, timestamp)
            ) PARTITION BY RANGE (timestamp);
            """,
            reverse_sql="DROP TABLE tracking_devicedata CASCADE;"
        ),
        # Create a default partition
        migrations.RunSQL(
            sql="""
            CREATE TABLE tracking_devicedata_default 
            PARTITION OF tracking_devicedata DEFAULT;
            """,
            reverse_sql="DROP TABLE tracking_devicedata_default;"
        ),
        # Re-create index for speed (optional)
        migrations.RunSQL(
            sql="CREATE INDEX idx_devicedata_device_id_time ON tracking_devicedata (device_id, timestamp DESC);",
            reverse_sql="DROP INDEX idx_devicedata_device_id_time;"
        ),
    ]
