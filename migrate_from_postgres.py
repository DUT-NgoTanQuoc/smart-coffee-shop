#!/usr/bin/env python
"""
Migrate data from PostgreSQL to SQLite
"""
import psycopg2
import sqlite3
from datetime import datetime

# PostgreSQL connection
try:
    pg_conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='coffee_shop',
        user='postgres',
        password='postgres'
    )
    pg_cursor = pg_conn.cursor()
    print("✓ Connected to PostgreSQL\n")
except Exception as e:
    print(f"✗ Failed to connect to PostgreSQL: {e}")
    exit(1)

# SQLite connection
sqlite_path = r"E:\Ki2nam3\PythonWeb\smart-coffee-shop\db.sqlite3"
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cursor = sqlite_conn.cursor()
print(f"✓ Connected to SQLite: {sqlite_path}\n")

print("=== Migrating Data ===\n")

try:
    # 1. Categories
    print("1. Migrating categories...")
    pg_cursor.execute("SELECT id, name, description FROM categories")
    categories = pg_cursor.fetchall()
    for cat_id, name, desc in categories:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO categories (id, name, description) VALUES (?, ?, ?)",
            (cat_id, name, desc)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(categories)} categories")

    # 2. Products
    print("2. Migrating products...")
    pg_cursor.execute("SELECT id, category_id, name, price, description, image FROM products")
    products = pg_cursor.fetchall()
    for prod_id, cat_id, name, price, desc, image in products:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO products (id, category_id, name, price, description, image) VALUES (?, ?, ?, ?, ?, ?)",
            (prod_id, cat_id, name, price, desc, image)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(products)} products")

    # 3. Ingredients
    print("3. Migrating ingredients...")
    pg_cursor.execute("SELECT id, name, unit, quantity FROM ingredients")
    ingredients = pg_cursor.fetchall()
    for ing_id, name, unit, qty in ingredients:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO ingredients (id, name, unit, quantity) VALUES (?, ?, ?, ?)",
            (ing_id, name, unit, qty)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(ingredients)} ingredients")

    # 4. Customers
    print("4. Migrating customers...")
    pg_cursor.execute("SELECT id, name, phone, email, points, tier FROM customers")
    customers = pg_cursor.fetchall()
    for cust_id, name, phone, email, points, tier in customers:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO customers (id, name, phone, email, points, tier) VALUES (?, ?, ?, ?, ?, ?)",
            (cust_id, name, phone, email, points, tier)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(customers)} customers")

    # 5. Orders
    print("5. Migrating orders...")
    pg_cursor.execute(
        "SELECT id, customer_id, staff_id, total, points_earned, points_used, order_status, created_at FROM orders"
    )
    orders = pg_cursor.fetchall()
    for order_id, cust_id, staff_id, total, pts_earned, pts_used, status, created_at in orders:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO orders (id, customer_id, staff_id, total, points_earned, points_used, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, cust_id, staff_id, total, pts_earned, pts_used, status, created_at)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(orders)} orders")

    # 6. Order Items
    print("6. Migrating order items...")
    pg_cursor.execute("SELECT id, order_id, product_id, quantity, price FROM order_items")
    order_items = pg_cursor.fetchall()
    for item_id, order_id, prod_id, qty, price in order_items:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO order_items (id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
            (item_id, order_id, prod_id, qty, price)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(order_items)} order items")

    # 7. Staff
    print("7. Migrating staff...")
    pg_cursor.execute("SELECT id, name, phone, email, role, salary, is_active FROM staff")
    staff_data = pg_cursor.fetchall()
    for staff_id, name, phone, email, role, salary, is_active in staff_data:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO staff (id, name, phone, email, role, salary, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (staff_id, name, phone, email, role, salary, is_active)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(staff_data)} staff members")

    # 8. Work Logs
    print("8. Migrating work logs...")
    pg_cursor.execute("SELECT id, staff_id, work_date, check_in, check_out, hours_worked FROM work_logs")
    work_logs = pg_cursor.fetchall()
    for log_id, staff_id, work_date, check_in, check_out, hours in work_logs:
        sqlite_cursor.execute(
            "INSERT OR REPLACE INTO work_logs (id, staff_id, work_date, check_in, check_out, hours_worked) VALUES (?, ?, ?, ?, ?, ?)",
            (log_id, staff_id, work_date, check_in, check_out, hours)
        )
    sqlite_conn.commit()
    print(f"   ✓ Inserted {len(work_logs)} work logs")

    print(f"\n✅ Data migration completed successfully!\n")

    # Verify
    print("=== Verification ===")
    sqlite_cursor.execute("SELECT COUNT(*) FROM products")
    print(f"Products: {sqlite_cursor.fetchone()[0]}")
    sqlite_cursor.execute("SELECT COUNT(*) FROM orders")
    print(f"Orders: {sqlite_cursor.fetchone()[0]}")
    sqlite_cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"Customers: {sqlite_cursor.fetchone()[0]}")
    sqlite_cursor.execute("SELECT COUNT(*) FROM staff")
    print(f"Staff: {sqlite_cursor.fetchone()[0]}")
    sqlite_cursor.execute("SELECT COUNT(*) FROM ingredients")
    print(f"Ingredients: {sqlite_cursor.fetchone()[0]}")

except Exception as e:
    print(f"\n✗ Error during migration: {e}")
    import traceback
    traceback.print_exc()
finally:
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
