#!/usr/bin/env python
"""
Script to rebuild accounts table with data and set password to 123456
"""
import os
import django
import sqlite3
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['USE_SQLITE'] = 'True'

django.setup()

from django.conf import settings

# Get DB path
db_path = settings.DATABASES['default']['NAME']
print(f"Database: {db_path}")

# Connect directly to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop old accounts table if exists
print("Dropping old accounts table...")
cursor.execute("DROP TABLE IF EXISTS accounts")
conn.commit()

# Create accounts table for SQLite
print("Creating new accounts table...")
create_table_sql = """
CREATE TABLE accounts (
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
conn.commit()

# Set password hash
initial_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"
print(f"Password hash for '123456': {initial_hash}")

# Insert sample accounts
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

print("\nInserting accounts...")
for acc_id, staff_id, username, pwd_hash, role_id in sample_accounts:
    cursor.execute(
        "INSERT INTO accounts (id, staff_id, username, password_hash, role_id) VALUES (?, ?, ?, ?, ?)",
        (acc_id, staff_id, username, pwd_hash, role_id)
    )
    print(f"  ✓ {username}")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM accounts")
count = cursor.fetchone()[0]

print(f"\n✅ Created {count} accounts with password: 123456")
print("\nSample accounts:")
cursor.execute("SELECT id, username, password_hash FROM accounts LIMIT 5")
for acc_id, username, hash_val in cursor.fetchall():
    print(f"  - ID {acc_id} ({username}): hash {hash_val[:30]}...")

conn.close()
print("\n🎉 Done! All accounts ready to use.")
print(f"\nYou can now login with:")
print(f"  Username: quan_ly, cashier1, cashier2, barista1-4, parttime")
print(f"  Password: 123456")
