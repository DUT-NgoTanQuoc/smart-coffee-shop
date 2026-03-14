import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sessions.models import Session
deleted, _ = Session.objects.all().delete()
print(f'Cleared {deleted} sessions. Browser will show login screen.')

