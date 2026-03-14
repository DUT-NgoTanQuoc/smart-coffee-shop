import os
import hashlib
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

COMMON_PASSWORDS = [
    '123456', 'password', '12345678', '1234', 'qwerty', '12345',
    'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master',
    'hello', 'freedom', 'whatever', 'qazwsx', 'admin123', 'Password123',
    'cashier123', 'barista1', 'barista123', 'parttime', '123123',
    '000000', '111111', 'manager', 'quanly', '123'
]

print("=== LIST ALL ACCOUNT HASHES ===")
print("-" * 50)

cursor = connection.cursor()
cursor.execute("""
    SELECT id, username, password_hash, role_id, is_active, is_locked 
    FROM accounts 
    ORDER BY username
""")
accounts = cursor.fetchall()

cracked = []

for account in accounts:
    acc_id, username, password_hash, role_id, is_active, is_locked = account
    clean_hash = password_hash.replace('$md5$', '') if password_hash.startswith('$md5$') else password_hash
    status = "✅" if is_active else "❌"
    locked = "🔒" if is_locked else ""
    
    print(f"ID: {acc_id} | Username: {username} | Hash: {clean_hash} {status} {locked}")
    
    # Try crack
    for pw in COMMON_PASSWORDS:
        if hashlib.md5(pw.encode()).hexdigest() == clean_hash:
            print(f"  → CRACKED: '{pw}'")
            cracked.append((username, pw))
            break

print("\n=== CRACKED PASSWORDS ===")
print("-" * 30)
if cracked:
    for user, pw in cracked:
        print(f"{user}: {pw}")
else:
    print("No common passwords cracked. Try stronger dictionary or rainbow tables.")

print("\n💡 NOTE: MD5 is BROKEN. Use Django PBKDF2/Argon2 in production!")
print("Run: python check_passwords.py")
