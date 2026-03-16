#!/usr/bin/env python
"""
Full restore: backup current DB, drop & recreate coffee_shop, load dump
"""
import os
import sys
import psycopg2
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings

DB_NAME = settings.DATABASES['default'].get('NAME', 'coffee_shop')
DB_USER = settings.DATABASES['default'].get('USER', 'postgres')
DB_PASSWORD = settings.DATABASES['default'].get('PASSWORD', 'password')
DB_HOST = settings.DATABASES['default'].get('HOST', 'localhost')
DB_PORT = settings.DATABASES['default'].get('PORT', '5432')

print(f"=== Full Restore: coffee_shop ===")
print(f"Database: {DB_NAME}")
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}\n")

# Step 1: Backup current DB
print("Step 1: Backing up current database...")
try:
    backup_file = f"database/coffee_shop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    os.makedirs('database', exist_ok=True)
    
    # Use pg_dump if available, else use psql
    import subprocess
    try:
        result = subprocess.run(
            f'pg_dump -h {DB_HOST} -U {DB_USER} -d {DB_NAME} > "{backup_file}"',
            shell=True,
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ Backup created: {backup_file}")
        else:
            print(f"⚠️  pg_dump failed: {result.stderr.decode()}")
    except Exception as e:
        print(f"⚠️  pg_dump not available: {e}")

except Exception as e:
    print(f"⚠️  Backup skipped: {e}")

# Step 2: Drop & recreate database
print("\nStep 2: Dropping and recreating database...")
try:
    admin_conn = psycopg2.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        database='postgres',
        port=DB_PORT
    )
    admin_conn.autocommit = True
    admin_cur = admin_conn.cursor()
    
    # Terminate existing connections
    admin_cur.execute(f"""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = '{DB_NAME}' AND pid != pg_backend_pid()
    """)
    print(f"  Terminated existing connections")
    
    # Drop database
    admin_cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    print(f"  Dropped database {DB_NAME}")
    
    # Recreate database
    admin_cur.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"✅ Created fresh database {DB_NAME}")
    
    admin_cur.close()
    admin_conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Step 3: Load dump into fresh database
print("\nStep 3: Loading dump file...")
import re

try:
    with open('database/schema_updated.sql', 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"❌ Cannot read dump: {e}")
    sys.exit(1)

# Clean up psql meta commands
content = re.sub(r'^\\.*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^\s*--.*$', '', content, flags=re.MULTILINE)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    print("  Executing SQL statements...")
    try:
        cur.execute(content)
        print(f"✅ Full dump loaded successfully!")
    except Exception as e:
        print(f"⚠️  Full execution failed, trying per-statement...")
        print(f"  Error: {e}\n")
        
        # Split into statements
        statements = []
        stmt = []
        i = 0
        L = len(content)
        in_squote = False
        in_dquote = False
        in_dollar = None

        while i < L:
            ch = content[i]
            if content[i] == '$':
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

        if stmt:
            s = ''.join(stmt).strip()
            if s:
                statements.append(s)

        print(f"  Total statements: {len(statements)}")
        executed = 0
        skipped = 0
        errors = 0
        for index, s in enumerate(statements, 1):
            try:
                cur.execute(s)
                executed += 1
            except Exception as e2:
                msg = str(e2).lower()
                if 'already exists' in msg or 'duplicate' in msg:
                    skipped += 1
                    continue
                errors += 1
                if errors <= 5:
                    print(f"    Statement {index} failed: {str(e2)[:80]}")
                if errors == 6:
                    print(f"    ... ({len(statements) - index} more statements)")

        print(f"\n✅ Execution finished:")
        print(f"  Executed: {executed}")
        print(f"  Skipped (already exist): {skipped}")
        print(f"  Failed: {errors}")
        print(f"  Total: {len(statements)}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ Restore complete!")
print("="*50)
print(f"\nServer can be started with:")
print(f"  python manage.py runserver 0.0.0.0:8000")
