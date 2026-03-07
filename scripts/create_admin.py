import os

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'adminpass')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created:', username)
else:
    print('Superuser already exists:', username)
