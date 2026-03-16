#!/usr/bin/env python
"""
Check which tables are empty and restore data from schema if needed
"""
import sqlite3

db_path = r"E:\Ki2nam3\PythonWeb\smart-coffee-shop\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print("=== Table Status ===\n")

empty_tables = []
populated_tables = []

for table in tables:
    if table.startswith('sqlite_'):
        continue
    
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    
    if count == 0:
        empty_tables.append(table)
        print(f"❌ {table}: EMPTY (0 rows)")
    else:
        populated_tables.append((table, count))
        print(f"✓ {table}: {count} rows")

print(f"\n📊 Summary:")
print(f"  Populated tables: {len(populated_tables)}")
print(f"  Empty tables: {len(empty_tables)}")

if empty_tables:
    print(f"\nEmpty tables:")
    for t in empty_tables:
        print(f"  - {t}")

conn.close()
