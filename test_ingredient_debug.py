#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Get or create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={'is_superuser': True, 'is_staff': True}
)
if created:
    admin_user.set_password('123456')
    admin_user.save()

client = Client()
client.login(username='admin', password='123456')

# Test with DEBUG = True to see errors
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    try:
        response = client.get('/ingredients/')
        print(f"Status: {response.status_code}")
        
        # Check for exceptions in response
        if hasattr(response, 'exc_info') and response.exc_info:
            print(f"Exception occurred: {response.exc_info}")
        
        # Try to render
        content = response.content.decode('utf-8')
        if 'Traceback' in content or 'Error' in content:
            # Find error message
            import re
            errors = re.findall(r'<h1[^>]*>(.*?)</h1>', content)
            if errors:
                print(f"Error message: {errors[0]}")
            
            # Print first 1000 chars of content
            print("\n--- Response Content (first 1000 chars) ---")
            print(content[:1000])
        else:
            print("✓ Page rendered without errors")
            print(f"Content length: {len(content)} bytes")
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
