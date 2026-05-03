import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.test import Client
c = Client()
logged = c.login(username='admin', password='admin123')
print('logged in:', logged)
r = c.get('/staff/schedule/')
print('status:', r.status_code)
print('has calendar:', '<div id="staffCalendar">' in r.content.decode('utf-8'))
open('scripts/schedule_page_auth.html','wb').write(r.content)
print('Saved to scripts/schedule_page_auth.html')
