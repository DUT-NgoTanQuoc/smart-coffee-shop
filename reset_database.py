import psycopg2

# Use environment variables or raw connection
try:
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',  # Connect to default database first
        user='postgres',
        password='password'  # Try default password
    )
except:
    print("Cannot connect with default password. Please provide correct password.")
    import sys
    sys.exit(1)

try:
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop existing database
    cursor.execute("DROP DATABASE IF EXISTS coffee_shop")
    print("Dropped coffee_shop database")
    
    # Create fresh database
    cursor.execute("CREATE DATABASE coffee_shop")
    print("Created fresh coffee_shop database")
    
    cursor.close()
    conn.close()
    
    print("\nNow run: python manage.py migrate")
    
except Exception as e:
    print(f"Error: {e}")
