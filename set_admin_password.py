import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Set admin password
admin = User.objects.get(username='admin')
admin.set_password('123456')
admin.save()

print(f"✅ Admin password set to: 123456")
print(f"Username: admin")
