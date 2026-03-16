#!/usr/bin/env python
import psycopg2
from psycopg2 import sql

try:
    # Kết nối tới PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='postgres',
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Terminate các connections khác tới coffee_shop
    cursor.execute("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = 'coffee_shop' AND pid != pg_backend_pid()
    """)
    result = cursor.fetchall()
    print(f"✅ Terminated {len(result)} connections to coffee_shop")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
