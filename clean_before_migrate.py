import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Delete all NULL names
    cursor.execute("DELETE FROM django_content_type WHERE name IS NULL")
    rows_deleted = cursor.rowcount
    print(f"Deleted {rows_deleted} rows with NULL names")
    
    # Now try migrate
    print("Attempting migrate...")
