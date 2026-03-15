import psycopg2
conn = psycopg2.connect(dbname='coffee_shop', user='postgres', password='postgres', host='localhost', port='5432')
cur = conn.cursor()
# Drop the not null constraint temporarily
cur.execute('ALTER TABLE django_content_type ALTER COLUMN name DROP NOT NULL')
conn.commit()
print('Dropped NOT NULL constraint')
cur.close()
conn.close()
