#!/usr/bin/env python
"""
Script to create accounts table on SQLite and reset all passwords to 123456
"""
import os
import django
import sqlite3
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['USE_SQLITE'] = 'True'

django.setup()

from django.conf import settings
from pathlib import Path

# Get DB path
db_path = settings.DATABASES['default']['NAME']
print(f"Database: {db_path}")

# Connect directly to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if accounts table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
table_exists = cursor.fetchone()

if table_exists:
    print("✓ Table 'accounts' already exists")
    # Get current accounts
    cursor.execute("SELECT id, username FROM accounts")
    accounts = cursor.fetchall()
    print(f"  Found {len(accounts)} accounts:")
    for acc_id, username in accounts:
        print(f"    - ID {acc_id}: {username}")
else:
    print("⚠ Table 'accounts' does NOT exist - creating it...")
    
    # Create accounts table for SQLite
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        staff_id INTEGER,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        is_locked BOOLEAN DEFAULT 0,
        failed_attempts SMALLINT DEFAULT 0,
        last_login TIMESTAMP,
        last_password_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    
    # Set initial password hash for all (will be updated below)
    initial_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"
    
    # Insert sample accounts from your DB view
    sample_accounts = [
        (1, 1, 'quan_ly', initial_hash, 1),
        (2, 2, 'cashier1', initial_hash, 2),
        (3, 3, 'cashier2', initial_hash, 2),
        (4, 4, 'barista1', initial_hash, 3),
        (5, 5, 'barista2', initial_hash, 3),
        (6, 6, 'barista3', initial_hash, 3),
        (7, 7, 'barista4', initial_hash, 3),
        (8, 8, 'parttime', initial_hash, 4),
    ]
    
    for acc_id, staff_id, username, pwd_hash, role_id in sample_accounts:
        cursor.execute(
            "INSERT INTO accounts (id, staff_id, username, password_hash, role_id) VALUES (?, ?, ?, ?, ?)",
            (acc_id, staff_id, username, pwd_hash, role_id)
        )
    
    conn.commit()
    print(f"✓ Created 'accounts' table with {len(sample_accounts)} sample accounts")

# Now reset all passwords
new_password_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"
print(f"\nResetting all passwords to: 123456")
print(f"Hash: {new_password_hash}")

cursor.execute("UPDATE accounts SET password_hash = ?", [new_password_hash])
conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM accounts")
count = cursor.fetchone()[0]
cursor.execute("SELECT id, username, password_hash FROM accounts LIMIT 10")
accounts = cursor.fetchall()

print(f"\n✅ Updated {count} accounts with new password!")
print("\nVerifying (first 10):")
for acc_id, username, hash_val in accounts:
    print(f"  ✓ ID {acc_id} ({username}): {hash_val[:20]}...")

conn.close()
print("\n🎉 Done!")
