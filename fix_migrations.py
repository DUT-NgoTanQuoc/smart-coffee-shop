import psycopg2

conn = psycopg2.connect(dbname='coffee_shop', user='postgres', password='300325', host='localhost', port='5432')
cur = conn.cursor()

# Mark all migrations as applied
apps = ['admin', 'analytics', 'auth', 'contenttypes', 'customers', 'ingredients', 'orders', 'products', 'sessions', 'staff']

for app in apps:
    cur.execute("SELECT 1 FROM django_migrations WHERE app = %s", (app,))
    if not cur.fetchone():
        cur.execute("INSERT INTO django_migrations (app, name, applied) VALUES (%s, '0001_initial', NOW())", (app,))

conn.commit()
print("All migrations marked as applied")

cur.execute("SELECT app, name FROM django_migrations ORDER BY id")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()

