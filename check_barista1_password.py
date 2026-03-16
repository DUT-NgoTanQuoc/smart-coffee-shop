#!/usr/bin/env python
"""
Check password hash for barista1
"""
import psycopg2
import hashlib

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='coffee_shop',
        user='postgres',
        password='postgres'
    )
    cursor = conn.cursor()
    
    print("=== Checking barista1 password ===\n")
    
    cursor.execute("SELECT id, username, password_hash FROM accounts WHERE username = 'barista1'")
    row = cursor.fetchone()
    
    if row:
        acc_id, username, pwd_hash = row
        print(f"Account: ID {acc_id}, Username: {username}")
        print(f"Hash in DB: {pwd_hash}\n")
        
        # Calculate hash for "123456"
        correct_hash = hashlib.md5('123456'.encode()).hexdigest()
        correct_hash_with_prefix = f"$md5${correct_hash}"
        
        print(f"Expected hash for '123456':")
        print(f"  Without prefix: {correct_hash}")
        print(f"  With $md5$ prefix: {correct_hash_with_prefix}\n")
        
        # Check if it matches
        clean_db_hash = pwd_hash.replace('$md5$', '') if pwd_hash.startswith('$md5$') else pwd_hash
        
        if clean_db_hash == correct_hash:
            print("✓ Hash MATCHES! Password should work.")
        else:
            print("✗ Hash MISMATCH!")
            print(f"  DB hash (without prefix): {clean_db_hash}")
            print(f"  Expected: {correct_hash}")
            
            # Update it
            print(f"\nUpdating password hash...")
            cursor.execute(
                "UPDATE accounts SET password_hash = %s WHERE username = 'barista1'",
                [correct_hash_with_prefix]
            )
            conn.commit()
            print("✓ Updated!")
    else:
        print("✗ Account 'barista1' not found!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
