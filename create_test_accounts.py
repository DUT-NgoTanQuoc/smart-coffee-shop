import os
import django
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import Account
from apps.staff.models import Staff

# Test accounts for different roles
test_accounts = [
    {'username': 'admin1', 'email': 'admin1@coffee.local', 'role': 'admin'},
    {'username': 'cashier1', 'email': 'cashier1@coffee.local', 'role': 'cashier'},
    {'username': 'barista1', 'email': 'barista1@coffee.local', 'role': 'barista'},
    {'username': 'barista2', 'email': 'barista2@coffee.local', 'role': 'barista'},
]

password = '123456'
md5_password = f'$md5${hashlib.md5(password.encode()).hexdigest()}'

print("Creating test accounts...")

for acc_data in test_accounts:
    username = acc_data['username']
    email = acc_data['email']
    role = acc_data['role']
    
    # Create Django User
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Django User: {username}")
    
    # Create Account (custom auth table)
    account, created = Account.objects.get_or_create(
        username=username,
        defaults={
            'password': md5_password,
            'email': email,
            'staff_id': None,  # Will link later
        }
    )
    if created:
        print(f"✅ Account: {username} (MD5 password)")
    
    # Create Staff
    staff, created = Staff.objects.get_or_create(
        name=username.title(),
        defaults={
            'email': email,
            'phone': f'09{username[-1]}{username[-1]}123456',
            'role': role,
            'is_active': True,
        }
    )
    if created:
        print(f"✅ Staff: {username} as {role}")
        
        # Link Account to Staff
        account.staff_id = staff.id
        account.save()
        print(f"   Linked Account → Staff")

print("\n" + "="*50)
print("Test Accounts Created:")
print("="*50)
for acc in test_accounts:
    print(f"{acc['username']:15} | {acc['role']:10} | password: {password}")
print("="*50)
