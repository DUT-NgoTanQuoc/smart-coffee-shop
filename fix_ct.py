#!/usr/bin/env python
"""Fix all content types"""
import psycopg2

DB = {
    'dbname': 'coffee_shop',
    'user': 'postgres',
    'password': '300325',
    'host': 'localhost',
    'port': '5432'
}

conn = psycopg2.connect(**DB)
cursor = conn.cursor()

# Fix all null/empty names
cursor.execute("UPDATE django_content_type SET name = INITCAP(REPLACE(model, '_', ' ')) WHERE name IS NULL OR name = ''")
conn.commit()
print('Fixed all null names')

cursor.execute('SELECT id, app_label, model, name FROM django_content_type ORDER BY id')
for r in cursor.fetchall():
    print(r)

cursor.close()
conn.close()

