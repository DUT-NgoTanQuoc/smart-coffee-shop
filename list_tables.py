import psycopg2

conn = psycopg2.connect('host=localhost user=postgres password=postgres dbname=coffee_shop')
cursor = conn.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in coffee_shop:")
for t in sorted(tables):
    print(f"  - {t}")
conn.close()
