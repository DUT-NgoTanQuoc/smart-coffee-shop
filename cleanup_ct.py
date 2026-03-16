import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Delete rows with NULL names
    cursor.execute("DELETE FROM django_content_type WHERE name IS NULL")
    print(f"Deleted {cursor.rowcount} rows with NULL names")
    
    # Show what's left
    cursor.execute("SELECT id, app_label, model FROM django_content_type")
    print("\nRemaining django_content_type rows:")
    for row in cursor.fetchall():
        print(f"  ID={row[0]}, app={row[1]}, model={row[2]}")
