import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType

# Fix null names in content_type
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT id, app_label, model FROM django_content_type WHERE name IS NULL
    """)
    rows = cursor.fetchall()
    
    for ct_id, app_label, model in rows:
        print(f"Fixing ContentType {ct_id}: {app_label}.{model}")
        # Generate proper name
        name = model.replace('_', ' ').title()
        cursor.execute(
            "UPDATE django_content_type SET name = %s WHERE id = %s",
            [name, ct_id]
        )
    
    if rows:
        connection.commit()
        print(f"\nFixed {len(rows)} ContentTypes")
    else:
        print("No NULL content types found")
