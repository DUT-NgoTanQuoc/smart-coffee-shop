#!/usr/bin/env python
"""
HƯỚNG DẪN SỬ DỤNG SMART COFFEE SHOP POS

Chạy chương trình:
  cd e:\Ki2nam3\PythonWeb\smart-coffee-shop
  python manage.py runserver 0.0.0.0:8000

Sau đó truy cập: http://127.0.0.1:8000
"""

import os
import sys

print("=" * 70)
print("🚀 SMART COFFEE SHOP - POINT OF SALE SYSTEM")
print("=" * 70)

print("\n📝 TÀI KHOẢN TEST:")
print("""
ADMIN (Quản lý)
  Username: admin
  Password: 123456
  Quyền: Quản lý toàn bộ hệ thống

CASHIER (Thu Ngân)
  Username: cashier1 hoặc cashier2
  Password: 123456
  Quyền: Tạo đơn hàng, xem danh sách đơn hàng

BARISTA (Pha chế)
  Username: barista1, barista2, barista3, barista4
  Password: 123456
  Quyền: Xử lý đơn hàng, quản lý nguyên liệu

PART-TIME
  Username: parttime
  Password: 123456
  Quyền: Quản lý nguyên liệu
""")

print("\n🔧 THIẾT LẬP:")
print("""
1. Server Django đang chạy ở: http://0.0.0.0:8000
2. Database: PostgreSQL (coffee_shop)
3. Dữ liệu test:
   - 20 sản phẩm
   - 150 đơn hàng
   - 50 khách hàng
   - 26 nguyên liệu
""")

print("\n📱 QÚLOC TRÌNH ĐĂNG NHẬP:")
print("""
1. Truy cập http://127.0.0.1:8000
2. Nhập username và password từ danh sách trên
3. Click Đăng nhập
4. Menu tự động thay đổi theo role của bạn
5. Chỉ thấy chức năng dành cho role của bạn
""")

print("\n🎯 CHỨC NĂNG THEO ROLE:")
print("""
┌─ ADMIN
│  ├─ Dashboard quản lý
│  ├─ Quản lý sản phẩm
│  ├─ Quản lý nguyên liệu
│  ├─ Quản lý khách hàng
│  ├─ Quản lý nhân viên
│  └─ Phân tích AI
│
├─ CASHIER
│  ├─ Tạo đơn hàng
│  ├─ Xem danh sách đơn hàng
│  └─ Bảng điều khiển thu ngân
│
└─ BARISTA
   ├─ Hàng chờ đơn hàng
   ├─ Quản lý nguyên liệu
   └─ Chi tiết nguyên liệu
""")

print("\n✅ HỆ THỐNG ĐÃ SẴN SÀNG!")
print("\n💡 Tip: Logout (Đăng xuất) để đổi tài khoản khác\n")

print("=" * 70)
