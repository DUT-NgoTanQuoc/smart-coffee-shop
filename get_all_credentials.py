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

cursor.execute('''
    SELECT a.id, a.username, s.name, s.role
    FROM accounts a
    JOIN staff s ON a.staff_id = s.id
    ORDER BY a.id
''')

rows = cursor.fetchall()

print('\n' + '='*120)
print(f"{'ID':<4} {'Tên đăng nhập':<25} {'Mật khẩu':<15} {'Tên nhân viên':<40} {'Vai trò':<15}")
print('='*120)

for row in rows:
    acc_id, username, name, role = row
    print(f"{acc_id:<4} {username:<25} {'123456':<15} {name:<40} {role:<15}")

print('='*120)
print(f"\n✅ Tổng cộng: {len(rows)} tài khoản\n")

cursor.close()
conn.close()
