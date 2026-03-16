#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Account

print("=== Django Users ===")
for user in User.objects.all():
    print(f"  {user.username}: superuser={user.is_superuser}, staff={user.is_staff}")

print("\n=== Custom Accounts ===")
for acc in Account.objects.all():
    print(f"  {acc.username}: role_id={acc.role_id}, active={acc.is_active}")

print("\n=== Roles (from role table if exists) ===")
try:
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute("SELECT id, name FROM roles LIMIT 10")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}")
except Exception as e:
    print(f"  Error: {e}")
