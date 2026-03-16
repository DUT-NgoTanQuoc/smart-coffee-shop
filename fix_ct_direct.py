import psycopg2

# Connect directly to PostgreSQL
conn = psycopg2.connect(
    host='localhost',
    database='coffee_shop',
    user='postgres',
    password='password'
)
cursor = conn.cursor()

try:
    # Fix all NULL names in django_content_type
    cursor.execute("""
        UPDATE django_content_type 
        SET name = initcap(replace(model, '_', ' '))
        WHERE name IS NULL
    """)
    
    print(f"Fixed {cursor.rowcount} content types")
    
    # Show remaining NULL values
    cursor.execute("SELECT id, app_label, model, name FROM django_content_type WHERE name IS NULL")
    remaining = cursor.fetchall()
    if remaining:
        print(f"\nStill NULL: {remaining}")
    else:
        print("All content types now have names")
    
    conn.commit()
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
