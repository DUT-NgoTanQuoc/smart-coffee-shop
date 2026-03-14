#!/usr/bin/env python
"""Fix all content types with null names - also fix newly created ones"""
import psycopg2

DB_PARAMS = {
    'dbname': 'coffee_shop',
    'user': 'postgres',
    'password': '300325',
    'host': 'localhost',
    'port': '5432'
}

def fix_content_types():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # Get all content types with null name and set a proper name
    cursor.execute(
        "SELECT id, app_label, model FROM django_content_type WHERE name IS NULL OR name = ''"
    )
    null_types = cursor.fetchall()
    
    print(f"Found {len(null_types)} content types with null/empty name:")
    
    for ct_id, app_label, model in null_types:
        # Create a name from model
        name = model.replace('_', ' ').title()
        cursor.execute(
            "UPDATE django_content_type SET name = %s WHERE id = %s",
            (name, ct_id)
        )
        print(f"  Updated: {app_label}.{model} -> '{name}'")
    
    conn.commit()
    
    # Verify - show all content types
    cursor.execute("SELECT id, app_label, model, name FROM django_content_type ORDER BY id")
    content_types = cursor.fetchall()
    
    print(f"\nAll content types ({len(content_types)}):")
    for ct in content_types:
        print(f"  {ct}")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    # Run multiple times to catch any new ones created by Django
    for i in range(3):
        print(f"\n=== Run {i+1} ===")
        fix_content_types()

