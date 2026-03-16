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

print("\n" + "="*80)
print("Xóa tài khoản admin khỏi Django User")
print("="*80)

# Kiểm tra trước
cursor.execute("SELECT id, username FROM auth_user WHERE username = 'admin'")
result = cursor.fetchone()

if result:
    user_id = result[0]
    print(f"\n✓ Tìm thấy user: admin (ID: {user_id})")
    
    # Xóa từ auth_user table
    cursor.execute("DELETE FROM auth_user WHERE username = 'admin'")
    conn.commit()
    
    print(f"✅ Đã xóa admin khỏi auth_user table")
    
    # Kiểm tra lại
    cursor.execute("SELECT id FROM auth_user WHERE username = 'admin'")
    if not cursor.fetchone():
        print("✅ Xác nhận: admin không còn trong hệ thống")
else:
    print("\n❌ Không tìm thấy user 'admin'")

print("\n" + "="*80)
print("Khi đăng nhập tiếp theo, bạn KHÔNG thể dùng admin/adminpass\n")

cursor.close()
conn.close()
