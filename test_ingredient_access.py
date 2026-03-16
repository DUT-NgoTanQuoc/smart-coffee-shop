#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Kiểm tra xem có user 'admin' không
try:
    admin_user = User.objects.get(username='admin')
    print(f"✓ Found admin user: {admin_user}")
except User.DoesNotExist:
    print("✗ Admin user not found, creating...")
    admin_user = User.objects.create_user(username='admin', password='123456')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print(f"✓ Created admin user: {admin_user}")

# Test client
client = Client()

# Test 1: Truy cập không đăng nhập
print("\n--- Test 1: Access without login ---")
response = client.get('/ingredients/')
print(f"Status: {response.status_code}")
if response.status_code == 302:
    print(f"Redirect to: {response.url}")

# Test 2: Đăng nhập và truy cập
print("\n--- Test 2: Access after login ---")
login_success = client.login(username='admin', password='123456')
print(f"Login success: {login_success}")

response = client.get('/ingredients/')
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✓ Page rendered successfully!")
    # Check if there are ingredients in context
    if 'ingredients' in response.context:
        count = len(response.context['ingredients'])
        print(f"✓ Found {count} ingredients in context")
    else:
        print("✗ No ingredients in context")
else:
    print(f"✗ Error status: {response.status_code}")
    print(f"Content: {response.content[:500]}")
