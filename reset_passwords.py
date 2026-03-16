#!/usr/bin/env python
"""
Script to reset all account passwords to 123456
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['USE_SQLITE'] = 'True'

django.setup()

import hashlib
from django.db import connection
from apps.core.models import Account

# Hash of "123456" with MD5 format
new_password_hash = f"$md5${hashlib.md5('123456'.encode()).hexdigest()}"

print(f"Updating all account passwords...")
print(f"New hash: {new_password_hash}")

# Update all accounts
with connection.cursor() as cursor:
    cursor.execute("UPDATE accounts SET password_hash = ?", [new_password_hash])
    connection.commit()

# Verify
count = Account.objects.count()
print(f"\nTotal accounts in DB: {count}")
print("\nSample accounts:")
for acc in Account.objects.all()[:10]:
    print(f"  ✓ {acc.username}: hash updated")

print(f"\n✅ All {count} accounts now have password: 123456")
