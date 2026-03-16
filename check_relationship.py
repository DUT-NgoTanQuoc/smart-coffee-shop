#!/usr/bin/env python
"""
Check relationship between accounts and staff tables
"""
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='coffee_shop',
        user='postgres',
        password='postgres'
    )
    cursor = conn.cursor()
    
    print("=== Accounts Table ===")
    cursor.execute("SELECT id, username, role_id, staff_id FROM accounts LIMIT 10")
    cols = [desc[0] for desc in cursor.description]
    print(f"Columns: {cols}\n")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    print("\n=== Staff Table ===")
    cursor.execute("SELECT id, name, email, role FROM staff LIMIT 10")
    cols = [desc[0] for desc in cursor.description]
    print(f"Columns: {cols}\n")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    print("\n=== Checking if staff_id in accounts points to staff.id ===")
    cursor.execute("""
        SELECT a.id, a.username, a.staff_id, s.id, s.name 
        FROM accounts a 
        LEFT JOIN staff s ON a.staff_id = s.id
        LIMIT 10
    """)
    for acc_id, username, staff_id, staff_real_id, staff_name in cursor.fetchall():
        print(f"Account {acc_id} ({username}): staff_id={staff_id} -> Staff {staff_real_id} ({staff_name})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
