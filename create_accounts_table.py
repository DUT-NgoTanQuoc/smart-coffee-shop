import psycopg2

# SQL để tạo accounts table (từ schema.sql)
create_accounts_sql = """
CREATE TABLE IF NOT EXISTS public.accounts (
    id integer NOT NULL PRIMARY KEY,
    staff_id integer,
    username character varying(50) NOT NULL UNIQUE,
    password_hash character varying(255) NOT NULL,
    role_id integer,
    is_active boolean DEFAULT true,
    is_locked boolean DEFAULT false,
    failed_attempts smallint DEFAULT 0,
    last_login timestamp without time zone,
    last_password_change timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE IF NOT EXISTS public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;
ALTER TABLE public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);
"""

conn = psycopg2.connect('host=localhost user=postgres password=postgres dbname=coffee_shop')
conn.autocommit = True
cursor = conn.cursor()

try:
    cursor.execute(create_accounts_sql)
    print("✅ accounts table created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
