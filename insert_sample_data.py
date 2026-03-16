#!/usr/bin/env python
"""
Insert sample data into empty tables for testing
"""
import sqlite3
from datetime import datetime, timedelta

db_path = r"E:\Ki2nam3\PythonWeb\smart-coffee-shop\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Inserting Sample Data ===\n")

# 1. Categories (Danh mục)
print("1. Categories...")
categories = [
    (1, 'Cà phê', 'Coffee products'),
    (2, 'Trà', 'Tea products'),
    (3, 'Nước ép', 'Juice products'),
    (4, 'Bánh', 'Pastries & snacks'),
]
for cat_id, name, desc in categories:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (id, name, description) VALUES (?, ?, ?)",
        (cat_id, name, desc)
    )
print(f"   Added {len(categories)} categories")

# 2. Products (Sản phẩm)
print("2. Products...")
products = [
    (1, 1, 'Espresso', 45000, 'Pure espresso shot'),
    (2, 1, 'Americano', 50000, 'Espresso with water'),
    (3, 1, 'Cappuccino', 55000, 'Espresso with milk foam'),
    (4, 1, 'Latte', 55000, 'Espresso with steamed milk'),
    (5, 2, 'Trà đen', 35000, 'Black tea'),
    (6, 2, 'Trà xanh', 35000, 'Green tea'),
    (7, 3, 'Nước cam', 40000, 'Orange juice'),
    (8, 4, 'Bánh croissant', 45000, 'French pastry'),
]
for prod_id, cat_id, name, price, desc in products:
    cursor.execute(
        "INSERT OR IGNORE INTO products (id, category_id, name, price, description) VALUES (?, ?, ?, ?, ?)",
        (prod_id, cat_id, name, price, desc)
    )
print(f"   Added {len(products)} products")

# 3. Ingredients (Nguyên liệu)
print("3. Ingredients...")
ingredients = [
    (1, 'Cà phê hạt', 'kg', 500),
    (2, 'Sữa tươi', 'l', 100),
    (3, 'Đường', 'kg', 50),
    (4, 'Nước lọc', 'l', 200),
]
for ing_id, name, unit, qty in ingredients:
    cursor.execute(
        "INSERT OR IGNORE INTO ingredients (id, name, unit, quantity) VALUES (?, ?, ?, ?)",
        (ing_id, name, unit, qty)
    )
print(f"   Added {len(ingredients)} ingredients")

# 4. Customers (Khách hàng)
print("4. Customers...")
customers = [
    (1, 'Nguyễn Văn A', '0912345678', 'a@example.com', 0, 'Đồng'),
    (2, 'Trần Thị B', '0987654321', 'b@example.com', 500, 'Bạc'),
    (3, 'Phạm Văn C', '0901234567', 'c@example.com', 2000, 'Vàng'),
]
for cust_id, name, phone, email, points, tier in customers:
    cursor.execute(
        "INSERT OR IGNORE INTO customers (id, name, phone, email, points, tier) VALUES (?, ?, ?, ?, ?, ?)",
        (cust_id, name, phone, email, points, tier)
    )
print(f"   Added {len(customers)} customers")

# 5. Orders (Đơn hàng)
print("5. Orders...")
orders = [
    (1, 1, 1, 150000, 0, 0, 'COMPLETED'),
    (2, 2, 1, 200000, 500, 0, 'COMPLETED'),
    (3, 3, None, 95000, 0, 0, 'PENDING'),
]
for order_id, customer_id, staff_id, total, points_earned, points_used, status in orders:
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT OR IGNORE INTO orders (id, customer_id, staff_id, total, points_earned, points_used, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (order_id, customer_id, staff_id, total, points_earned, points_used, status, now)
    )
print(f"   Added {len(orders)} orders")

# 6. Order Items (Chi tiết đơn)
print("6. Order Items...")
order_items = [
    (1, 1, 1, 2, 45000),  # Order 1: 2x Espresso
    (2, 1, 3, 1, 55000),  # Order 1: 1x Cappuccino
    (3, 2, 4, 2, 55000),  # Order 2: 2x Latte
    (4, 3, 1, 1, 45000),  # Order 3: 1x Espresso
]
for item_id, order_id, product_id, qty, price in order_items:
    cursor.execute(
        "INSERT OR IGNORE INTO order_items (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
        (item_id, order_id, product_id, qty, price)
    )
print(f"   Added {len(order_items)} order items")

# 7. Staff (Nhân viên)
print("7. Staff...")
staff_data = [
    (1, 'Quản lý', '0912345670', 'manager@coffee.com', 'manager', 15000000, 'ACTIVE'),
    (2, 'Người thu ngân 1', '0912345671', 'cashier1@coffee.com', 'cashier', 8000000, 'ACTIVE'),
    (3, 'Người thu ngân 2', '0912345672', 'cashier2@coffee.com', 'cashier', 8000000, 'ACTIVE'),
    (4, 'Barista 1', '0912345673', 'barista1@coffee.com', 'barista', 7000000, 'ACTIVE'),
    (5, 'Barista 2', '0912345674', 'barista2@coffee.com', 'barista', 7000000, 'ACTIVE'),
    (6, 'Barista 3', '0912345675', 'barista3@coffee.com', 'barista', 7000000, 'ACTIVE'),
    (7, 'Barista 4', '0912345676', 'barista4@coffee.com', 'barista', 7000000, 'ACTIVE'),
    (8, 'Part-time', '0912345677', 'parttime@coffee.com', 'parttime', 5000000, 'ACTIVE'),
]
for staff_id, name, phone, email, role, salary, is_active in staff_data:
    cursor.execute(
        "INSERT OR IGNORE INTO staff (id, name, phone, email, role, salary, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (staff_id, name, phone, email, role, salary, is_active == 'ACTIVE')
    )
print(f"   Added {len(staff_data)} staff members")

conn.commit()
print(f"\n✅ Sample data inserted successfully!")

# Verify
cursor.execute("SELECT COUNT(*) FROM products")
print(f"\nVerification:")
print(f"  - Products: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM orders")
print(f"  - Orders: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM customers")
print(f"  - Customers: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM staff")
print(f"  - Staff: {cursor.fetchone()[0]}")

conn.close()
