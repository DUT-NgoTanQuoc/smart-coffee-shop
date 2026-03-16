#!/usr/bin/env python
"""
Reset ALL account passwords properly to 123456
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
    
    print("=== Resetting ALL account passwords to 123456 ===\n")
    
    # Calculate correct hash for "123456"
    correct_hash = hashlib.md5('123456'.encode()).hexdigest()
    correct_hash_with_prefix = f"$md5${correct_hash}"
    
    print(f"New password: 123456")
    print(f"Hash: {correct_hash}\n")
    
    # Get all accounts first
    cursor.execute("SELECT id, username, password_hash FROM accounts ORDER BY id")
    accounts = cursor.fetchall()
    
    print("Current accounts:")
    for acc_id, username, old_hash in accounts:
        print(f"  ID {acc_id}: {username} - {old_hash[:40]}...")
    
    # Update ALL passwords
    print(f"\n=== Updating all passwords ===")
    cursor.execute(
        "UPDATE accounts SET password_hash = %s",
        [correct_hash_with_prefix]
    )
    conn.commit()
    print(f"✓ Updated {cursor.rowcount} accounts\n")
    
    # Verify
    print("=== After update ===")
    cursor.execute("SELECT id, username, password_hash FROM accounts ORDER BY id")
    for acc_id, username, new_hash in cursor.fetchall():
        status = "✓" if new_hash == correct_hash_with_prefix else "✗"
        print(f"  {status} ID {acc_id}: {username} - {new_hash[:40]}...")
    
    cursor.close()
    conn.close()
    print("\n✅ All passwords reset to 123456!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
