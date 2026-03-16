#!/usr/bin/env python
import psycopg2

conn = psycopg2.connect(
    dbname='coffee_shop',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# Kiểm tra Django User table
print("\n" + "="*90)
print("DJANGO USER TABLE (auth_user):")
print("="*90)

cursor.execute("SELECT id, username, email, is_superuser, is_staff, is_active FROM auth_user ORDER BY id")
rows = cursor.fetchall()

if rows:
    for row in rows:
        uid, username, email, is_superuser, is_staff, is_active = row
        print(f"ID: {uid}, Username: '{username}', Email: '{email}'")
        print(f"   Superuser: {is_superuser}, Staff: {is_staff}, Active: {is_active}\n")
else:
    print("❌ Không có user nào trong auth_user table")

# Kiểm tra accounts table
print("\n" + "="*90)
print("ACCOUNTS TABLE (custom):")
print("="*90)

cursor.execute("SELECT id, username, role_id, is_active FROM accounts ORDER BY id")
rows = cursor.fetchall()

if rows:
    for row in rows:
        acc_id, username, role_id, is_active = row
        print(f"ID: {acc_id}, Username: '{username}', Role: {role_id}, Active: {is_active}")
else:
    print("❌ Không có account nào trong accounts table")

print("\n" + "="*90)

cursor.close()
conn.close()
