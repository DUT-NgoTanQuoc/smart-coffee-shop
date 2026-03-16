#!/usr/bin/env python
"""
Reset PostgreSQL database - Drop and recreate coffee_shop database
"""
import psycopg2
import sys

DB_PARAMS = {
    'host': 'localhost',
    'database': 'postgres',  # Connect to default postgres database
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'
}

try:
    # Connect to postgres database
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Connecting to PostgreSQL...")
    
    # Terminate existing connections to coffee_shop database
    print("Terminating existing connections to coffee_shop...")
    cursor.execute("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'coffee_shop'
        AND pid <> pg_backend_pid()
    """)
    
    # Drop database
    print("Dropping coffee_shop database...")
    cursor.execute("DROP DATABASE IF EXISTS coffee_shop")
    
    # Create fresh database
    print("Creating fresh coffee_shop database...")
    cursor.execute("CREATE DATABASE coffee_shop WITH ENCODING 'UTF8'")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Database reset successfully!")
    print("Now run: python manage.py migrate")
    
except psycopg2.OperationalError as e:
    print(f"❌ Connection Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
