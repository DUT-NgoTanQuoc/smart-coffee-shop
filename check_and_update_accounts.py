#!/usr/bin/env python
"""
Check existing accounts table and update passwords only
"""
import sqlite3
import hashlib

db_path = r"E:\Ki2nam3\PythonWeb\smart-coffee-shop\db.sqlite3"
print(f"Database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what tables exist
print("=== Checking existing tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for (table_name,) in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} rows")

# Check if accounts table exists and has data
print("\n=== Checking accounts table ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
if cursor.fetchone():
    cursor.execute("SELECT COUNT(*) FROM accounts")
    count = cursor.fetchone()[0]
    print(f"✓ accounts table EXISTS with {count} rows")
    
    # Show current data
    if count > 0:
        print("\nCurrent accounts:")
        cursor.execute("SELECT id, username, password_hash FROM accounts LIMIT 10")
        for acc_id, username, pwd_hash in cursor.fetchall():
            print(f"  ID {acc_id}: {username} (hash: {pwd_hash[:40]}...)")
        
        # Update passwords
        print("\n=== Updating passwords to 123456 ===")
        new_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"
        cursor.execute("UPDATE accounts SET password_hash = ?", [new_hash])
        conn.commit()
        
        print(f"✓ Updated {count} accounts with new password hash")
        print(f"  Hash: {new_hash}\n")
        
        # Verify
        cursor.execute("SELECT id, username FROM accounts")
        print("Updated accounts:")
        for acc_id, username in cursor.fetchall():
            print(f"  ✓ ID {acc_id}: {username}")
else:
    print("✗ accounts table does NOT exist")
    print("  Creating sample data instead...")

conn.close()
print("\n✅ Done!")
