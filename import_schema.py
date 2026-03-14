#!/usr/bin/env python
"""Script to import database schema into PostgreSQL"""
import os
import sys
import psycopg2
from pathlib import Path

# Add Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent))

# Database connection parameters from .env
DB_PARAMS = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '300325',
    'host': 'localhost',
    'port': '5432'
}

def create_database():
    """Create coffee_shop database if not exists"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'coffee_shop'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'coffee_shop'...")
            cursor.execute("CREATE DATABASE coffee_shop")
            print("Database created successfully!")
        else:
            print("Database 'coffee_shop' already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def import_schema():
    """Import schema.sql into the database"""
    schema_path = Path(__file__).parent / 'database' / 'schema.sql'
    
    # Connect to coffee_shop database
    db_params = DB_PARAMS.copy()
    db_params['dbname'] = 'coffee_shop'
    
    try:
        print("Connecting to coffee_shop database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True  # Need autocommit for some operations
        cursor = conn.cursor()
        
        print(f"Reading schema from {schema_path}...")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Check if tables exist
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()[0]
        
        if table_count > 0:
            print(f"Found {table_count} tables in database. Schema already imported.")
            print("Skipping schema import to avoid duplicate tables.")
        else:
            print("Importing schema...")
            cursor.execute(schema_sql)
            print("Schema imported successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error importing schema: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 50)
    print("Database Schema Import Script")
    print("=" * 50)
    
    create_database()
    import_schema()
    
    print("=" * 50)
    print("Done!")
    print("=" * 50)

