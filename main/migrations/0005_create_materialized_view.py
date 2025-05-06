# Generated manually on 2025-05-06 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_closure_depth"),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW unit_hierarchy AS
            WITH RECURSIVE unit_cte AS (
                SELECT id, name, parent_id, 0 AS depth
                FROM main_unit
                WHERE parent_id IS NULL
                UNION ALL
                SELECT u.id, u.name, u.parent_id, uc.depth + 1
                FROM main_unit u
                INNER JOIN unit_cte uc ON u.parent_id = uc.id
            )
            SELECT * FROM unit_cte;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS unit_hierarchy;"
        ),
    ]