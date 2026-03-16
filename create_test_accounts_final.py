#!/usr/bin/env python
import os
import django
import hashlib
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.staff.models import Staff
from django.db import connection

# Xóa dữ liệu cũ
Staff.objects.all().delete()

# Tạo test staff
accounts_data = [
    {'username': 'admin', 'password': '123456', 'role': 'manager'},
    {'username': 'cashier1', 'password': '123456', 'role': 'cashier'},
    {'username': 'barista1', 'password': '123456', 'role': 'barista'},
    {'username': 'barista2', 'password': '123456', 'role': 'barista'},
]

cursor = connection.cursor()

# Xóa accounts cũ
cursor.execute("DELETE FROM accounts")

for idx, data in enumerate(accounts_data, 1):
    # Tạo Staff
    staff = Staff.objects.create(
        name=data['username'],
        phone=f"090{1000000 + idx}",
        role=data['role'],
        hire_date=date.today(),
        is_active=True
    )
    
    # Tạo Account trong database
    pwd_hash = hashlib.md5(data['password'].encode()).hexdigest()
    cursor.execute(
        """INSERT INTO accounts (id, username, password_hash, staff_id, role_id, is_active)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (idx, data['username'], pwd_hash, staff.id, None, True)
    )
    
    print(f"✅ Tạo tài khoản: {data['username']} / {data['password']} ({data['role']})")

connection.commit()
cursor.close()

print(f"\n✅ Hoàn tất! Tổng cộng: {len(accounts_data)} accounts")

