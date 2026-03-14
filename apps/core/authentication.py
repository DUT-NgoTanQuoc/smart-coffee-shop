from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db import connection
import hashlib
from .models import Account

class CustomAccountBackend(BaseBackend):
    """
    Custom authentication backend for accounts table (MD5 hashed passwords)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('user')
        if password is None:
            return None
        
        User = get_user_model()
        
        try:
            # Try Django User first (superuser)
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        
        # Check custom accounts table
        with connection.cursor() as cursor:
            # Query accounts
            cursor.execute("""
                SELECT id, username, password_hash, is_active, is_locked, failed_attempts 
                FROM accounts WHERE username = %s
            """, [username])
            
            row = cursor.fetchone()
            
            if row:
                account_id, username, password_hash, is_active, is_locked, failed_attempts = row
                
                # Remove $md5$ prefix if exists
                clean_hash = password_hash.replace('$md5$', '') if password_hash.startswith('$md5$') else password_hash
                
                if not is_locked and hashlib.md5(password.encode()).hexdigest() == clean_hash:
                    # Create user-like object
                    user = type('AccountUser', (), {
                        'id': account_id,
                        'username': username,
                        'is_authenticated': True,
                        'is_active': is_active,
                        'is_staff': username == 'quan_ly',  # Manager is staff
                        'is_superuser': False,
                        'backend': self.__class__.__name__,
                        '_meta': type('Meta', (), {'pk': lambda self: account_id})(),
                    })()
                    
                    # Update last_login (optional)
                    try:
                        cursor.execute("""
                            UPDATE accounts SET last_login = NOW(), failed_attempts = 0 
                            WHERE id = %s
                        """, [account_id])
                    except:
                        pass
                    
                    return user
                else:
                    # Increment failed attempts
                    try:
                        cursor.execute("""
                            UPDATE accounts SET failed_attempts = failed_attempts + 1 
                            WHERE id = %s
                        """, [account_id])
                    except:
                        pass
                        
        return None

    def get_user(self, user_id):
        """
        Get full user by ID from accounts table for session persistence
        """
        if not isinstance(user_id, int):
            return None
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, password_hash, is_active, is_locked, failed_attempts 
                FROM accounts WHERE id = %s
            """, [user_id])
            
            row = cursor.fetchone()
            
            if row:
                account_id, username, _, is_active, is_locked, _ = row
                
                # Create complete mock user
                user = type('AccountUser', (), {
                    'id': account_id,
                    'username': username,
                    'is_authenticated': True,
                    'is_active': is_active,
                    'is_staff': username == 'quan_ly',
                    'is_superuser': username == 'admin' or username == 'quan_ly',
                    'backend': self.__class__.__name__,
                    'has_perm': lambda self, perm=None, obj=None: self.is_superuser,
                    'has_perms': lambda self, perm_list, obj=None: all(self.has_perm(perm, obj) for perm in perm_list),
                    'has_module_perms': lambda self, app_label: self.is_superuser,
                    'get_username': lambda self: self.username,
                    '_meta': type('Meta', (), {'pk': property(lambda self: user_id)})(),
                })()
                return user
        
        return None

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_superuser

    def has_module_perms(self, app_label):
        return True

