import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

print("Fixing NULL content type names...")

with connection.cursor() as cursor:
    # First, check what's NULL
    cursor.execute("SELECT id, app_label, model FROM django_content_type WHERE name IS NULL")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} ContentTypes with NULL names")
    
    for ct_id, app_label, model in rows:
        proper_name = model.replace('_', ' ').title()
        print(f"  Fixing {app_label}.{model} -> '{proper_name}'")
        cursor.execute(
            "UPDATE django_content_type SET name = %s WHERE id = %s",
            [proper_name, ct_id]
        )

print("Done!")
