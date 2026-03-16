#!/usr/bin/env python
"""
Restore database schema and data from a pg_dump SQL file (psql-format).
This script:
 - Ensures the target database exists (creates if missing)
 - Loads the SQL file into the target database after stripping psql meta-commands

Usage: python restore_schema.py database/dump.sql

Be careful: this will execute SQL statements on the database. Make sure you have backups.
"""
import sys
import os
import re
import psycopg2
from psycopg2 import sql

# Read django settings to get default DB connection if available
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    from django.conf import settings
    DB = settings.DATABASES['default']
    DB_NAME = DB.get('NAME', 'coffee_shop')
    DB_USER = DB.get('USER', 'postgres')
    DB_PASSWORD = DB.get('PASSWORD', 'password')
    DB_HOST = DB.get('HOST', 'localhost')
    DB_PORT = DB.get('PORT', '5432')
except Exception:
    # Fallback defaults
    DB_NAME = 'coffee_shop'
    DB_USER = 'postgres'
    DB_PASSWORD = 'password'
    DB_HOST = 'localhost'
    DB_PORT = '5432'

if len(sys.argv) < 2:
    print('Usage: python restore_schema.py path/to/schema.sql')
    sys.exit(1)

dump_path = sys.argv[1]
if not os.path.exists(dump_path):
    print(f'File not found: {dump_path}')
    sys.exit(1)

print(f"Restore: file={dump_path} -> database={DB_NAME} host={DB_HOST} user={DB_USER}")

# Step 1: connect to postgres database to ensure target DB exists
try:
    admin_conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database='postgres', port=DB_PORT)
    admin_conn.autocommit = True
    admin_cur = admin_conn.cursor()
    admin_cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = admin_cur.fetchone() is not None
    if not exists:
        print(f"Database {DB_NAME} does not exist - creating it")
        admin_cur.execute(sql.SQL("CREATE DATABASE {}".format(sql.Identifier(DB_NAME).string)))
    else:
        print(f"Database {DB_NAME} exists")
    admin_cur.close()
    admin_conn.close()
except Exception as e:
    print(f"Failed to check/create database: {e}")
    sys.exit(1)

# Step 2: read dump and sanitize
try:
    with open(dump_path, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"Failed to read dump: {e}")
    sys.exit(1)

# Remove psql meta commands (lines starting with backslash)
content = re.sub(r'^\\.*$', '', content, flags=re.MULTILINE)
# Keep dollar-quoted function bodies intact. We'll remove only lines that are full-line SQL comments -- ...
content = re.sub(r'^\s*--.*$', '', content, flags=re.MULTILINE)

# Some dumps include SET search_path or SELECT pg_catalog.set_config - these are safe to keep, but
# some include \\connect or other meta commands; we removed backslash lines above.
try:
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
    conn.autocommit = True
    cur = conn.cursor()
    print('Executing SQL dump (this may take a while) ...')
    try:
        cur.execute(content)
        print('✅ SQL executed successfully')
    except Exception as e:
        # If full execution fails (common when objects already exist), try executing statement-by-statement
        print('Full execution failed, falling back to per-statement execution. Error:')
        print(e)
        print('\nSplitting SQL into statements (respecting $$ blocks)')

        statements = []
        stmt = []
        i = 0
        L = len(content)
        in_squote = False
        in_dquote = False
        in_dollar = None

        while i < L:
            ch = content[i]
            # detect dollar-quoted tag
            if content[i] == '$':
                # try to read tag
                m = re.match(r"\$[A-Za-z0-9_]*\$", content[i:])
                if m:
                    tag = m.group(0)
                    if in_dollar is None:
                        in_dollar = tag
                        stmt.append(tag)
                        i += len(tag)
                        continue
                    elif in_dollar == tag:
                        in_dollar = None
                        stmt.append(tag)
                        i += len(tag)
                        continue
            if in_dollar is not None:
                stmt.append(ch)
                i += 1
                continue

            if ch == "'" and not in_dquote:
                in_squote = not in_squote
                stmt.append(ch)
                i += 1
                continue
            if ch == '"' and not in_squote:
                in_dquote = not in_dquote
                stmt.append(ch)
                i += 1
                continue

            if ch == ';' and not in_squote and not in_dquote:
                stmt.append(ch)
                statements.append(''.join(stmt).strip())
                stmt = []
                i += 1
                continue

            stmt.append(ch)
            i += 1

        # remaining
        if stmt:
            s = ''.join(stmt).strip()
            if s:
                statements.append(s)

        print(f'Total statements: {len(statements)}')
        executed = 0
        skipped = 0
        for index, s in enumerate(statements, 1):
            try:
                cur.execute(s)
                executed += 1
            except Exception as e2:
                msg = str(e2).lower()
                # Skip common 'already exists' errors
                if 'already exists' in msg or 'duplicate' in msg:
                    skipped += 1
                    continue
                # For other errors, print and continue so restore can proceed partially
                print(f"Statement {index} failed: {e2}")
        print(f'Execution finished: executed={executed}, skipped={skipped}, total={len(statements)}')

    cur.close()
    conn.close()
except Exception as e:
    print('❌ Error executing SQL:')
    print(e)
    sys.exit(1)
