import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'django_content_type'
    """)
    print("django_content_type columns:")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    print("\nAll rows in django_content_type:")
    cursor.execute("SELECT id, app_label, model FROM django_content_type")
    for row in cursor.fetchall():
        print(f"  ID={row[0]}, app={row[1]}, model={row[2]}")
