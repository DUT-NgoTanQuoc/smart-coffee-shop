import psycopg2

conn = psycopg2.connect(dbname='coffee_shop', user='postgres', password='300325', host='localhost', port='5432')
cur = conn.cursor()

# First clear the table
cur.execute("TRUNCATE django_content_type CASCADE")
print("Cleared django_content_type table")

# Insert all content types that will be created by Django
# Based on all Django models in the project
content_types = [
    # Django contrib
    (1, 'admin', 'logentry', 'Logentry'),
    (2, 'auth', 'group', 'Group'),
    (3, 'auth', 'permission', 'Permission'),
    (4, 'auth', 'user', 'User'),
    (5, 'contenttypes', 'contenttype', 'Contenttype'),
    (6, 'sessions', 'session', 'Session'),
    # Local apps
    (7, 'core', 'account', 'Account'),
    (8, 'core', 'role', 'Role'),
    (9, 'core', 'permission', 'Permission'),
    (10, 'core', 'rolepermission', 'Rolepermission'),
    (11, 'core', 'refreshtoken', 'Refresh Token'),
    (12, 'core', 'auditlog', 'Audit Log'),
    (13, 'products', 'category', 'Category'),
    (14, 'products', 'product', 'Product'),
    (15, 'products', 'recipe', 'Recipe'),
    (16, 'products', 'customization', 'Customization'),
    (17, 'ingredients', 'ingredient', 'Ingredient'),
    (18, 'customers', 'customer', 'Customer'),
    (19, 'customers', 'favoritedrink', 'Favorite Drink'),
    (20, 'staff', 'staff', 'Staff'),
    (21, 'staff', 'worklog', 'Worklog'),
    (22, 'orders', 'order', 'Order'),
    (23, 'orders', 'orderitem', 'Order Item'),
    (24, 'orders', 'payment', 'Payment'),
    (25, 'analytics', 'dailystat', 'Daily Stat'),
]

for ct in content_types:
    cur.execute(
        "INSERT INTO django_content_type (id, app_label, model, name) VALUES (%s, %s, %s, %s)",
        ct
    )

conn.commit()
print(f"Inserted {len(content_types)} content types")

cur.execute("SELECT id, app_label, model, name FROM django_content_type ORDER BY id")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()

