#!/usr/bin/env python
"""Setup test accounts với role đúng cho ingredient access"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Test accounts
accounts = [
    {'username': 'admin', 'password': '123456', 'is_superuser': True, 'is_staff': True},
    {'username': 'cashier1', 'password': '123456', 'is_superuser': False, 'is_staff': False},
    {'username': 'barista1', 'password': '123456', 'is_superuser': False, 'is_staff': False},
]

for acc in accounts:
    try:
        user = User.objects.get(username=acc['username'])
        print(f"✓ {acc['username']} already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=acc['username'],
            password=acc['password'],
            is_superuser=acc['is_superuser'],
            is_staff=acc['is_staff']
        )
        print(f"✓ Created {acc['username']}")

print("\n--- Test Access ---")
from django.test import Client

test_cases = [
    ('admin', '123456', 'Should have access'),
    ('barista1', '123456', 'Should have access'),
    ('cashier1', '123456', 'Should be forbidden'),
    ('', '', 'Should redirect to login'),
]

client = Client()
for username, password, expected in test_cases:
    print(f"\nTesting {username or 'anonymous'}...")
    
    if username:
        client.login(username=username, password=password)
    
    response = client.get('/ingredients/')
    
    if response.status_code == 200:
        print(f"  ✓ Status 200 - {expected}")
    elif response.status_code == 403:
        print(f"  ✓ Status 403 (Forbidden) - User doesn't have permission")
    elif response.status_code == 302:
        print(f"  ✓ Status 302 (Redirect) - {response.url}")
    else:
        print(f"  ✗ Status {response.status_code}")
    
    client.logout()

print("\n✓ Setup complete!")
