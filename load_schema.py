#!/usr/bin/env python
import os
import sys
import django
import psycopg2
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Đọc schema.sql
with open('database/schema.sql', 'r', encoding='utf-8') as f:
    schema_content = f.read()

# Lọc meta commands (\\...) - psql specific
import re
schema_content = re.sub(r'^\\.*$', '', schema_content, flags=re.MULTILINE)
schema_content = re.sub(r'--.*$', '', schema_content, flags=re.MULTILINE)

# Kết nối PostgreSQL
conn = psycopg2.connect(
    host=settings.DATABASES['default']['HOST'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    database=settings.DATABASES['default']['NAME'],
    port=settings.DATABASES['default']['PORT']
)
conn.autocommit = True
cursor = conn.cursor()

try:
    # Thi hành schema
    cursor.execute(schema_content)
    print("✅ Schema loaded successfully!")
except Exception as e:
    print(f"❌ Error loading schema: {e}")
finally:
    cursor.close()
    conn.close()
