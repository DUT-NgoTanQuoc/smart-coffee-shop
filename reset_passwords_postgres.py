#!/usr/bin/env python
"""
Reset all account passwords to 123456 (except admin) in PostgreSQL
"""
import os
import django
import psycopg2
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# PostgreSQL connection
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='coffee_shop',
        user='postgres',
        password='postgres'
    )
    cursor = conn.cursor()
    print("✓ Connected to PostgreSQL\n")
except Exception as e:
    print(f"✗ Failed to connect: {e}")
    exit(1)

# Hash for "123456"
new_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"
print(f"New password hash: {new_hash}\n")

# Get all accounts except admin
print("=== Current accounts ===")
cursor.execute("SELECT id, username, password_hash FROM accounts WHERE username != 'admin' ORDER BY id")
accounts = cursor.fetchall()

if not accounts:
    print("⚠ No accounts found (excluding admin)")
else:
    print(f"Found {len(accounts)} accounts to update:\n")
    for acc_id, username, old_hash in accounts:
        print(f"  - ID {acc_id}: {username}")
        print(f"    Old: {old_hash[:40]}...")
    
    # Update passwords
    print(f"\n=== Updating passwords ===")
    cursor.execute(
        "UPDATE accounts SET password_hash = %s WHERE username != 'admin'",
        [new_hash]
    )
    conn.commit()
    print(f"✓ Updated {cursor.rowcount} accounts\n")
    
    # Verify
    print("=== Verification ===")
    cursor.execute("SELECT id, username, password_hash FROM accounts ORDER BY id")
    for acc_id, username, pwd_hash in cursor.fetchall():
        status = "🔐 unchanged (admin)" if username == 'admin' else "✓ updated"
        print(f"  {status}: ID {acc_id} ({username})")

cursor.close()
conn.close()
print("\n✅ Done!")
