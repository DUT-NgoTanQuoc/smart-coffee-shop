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
                account_id, db_username, password_hash, is_active, is_locked, failed_attempts = row
                
                # Remove $md5$ prefix if exists
                clean_hash = password_hash.replace('$md5$', '') if password_hash.startswith('$md5$') else password_hash
                
                if not is_locked and hashlib.md5(password.encode()).hexdigest() == clean_hash:
                    # Create user-like object with proper _meta structure
                    class AccountUser:
                        def __init__(self, account_id, username, is_active, is_staff, is_superuser):
                            self.id = account_id
                            self.username = username
                            self.is_authenticated = True
                            self.is_active = is_active
                            self.is_staff = is_staff
                            self.is_superuser = is_superuser
                            self.backend = self.__class__.__module__ + '.' + self.__class__.__name__
                            
                            # Create proper _meta.pk structure for Django session
                            class PK:
                                def value_to_string(self, obj):
                                    return str(obj.id)
                            
                            class Meta:
                                pk = PK()
                            
                            self._meta = Meta()
                        
                        def save(self, *args, **kwargs):
                            # No-op save for Django auth compatibility
                            pass
                        
                        def delete(self, *args, **kwargs):
                            # No-op delete for Django auth compatibility
                            pass
                    
                    user = AccountUser(
                        account_id=account_id,
                        username=db_username,
                        is_active=is_active,
                        is_staff=db_username == 'quan_ly',  # Manager is staff
                        is_superuser=False
                    )
                    
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
                account_id, db_username, _, is_active, is_locked, _ = row
                
                # Create complete mock user with proper _meta structure
                class AccountUser:
                    def __init__(self, account_id, username, is_active, is_staff, is_superuser):
                        self.id = account_id
                        self.username = username
                        self.is_authenticated = True
                        self.is_active = is_active
                        self.is_staff = is_staff
                        self.is_superuser = is_superuser
                        self.backend = 'apps.core.authentication.CustomAccountBackend'
                        
                        # Create proper _meta.pk structure
                        class PK:
                            def value_to_string(self, obj):
                                return str(obj.id)
                        
                        class Meta:
                            pk = PK()
                        
                        self._meta = Meta()
                    
                    def has_perm(self, perm=None, obj=None):
                        return self.is_superuser
                    
                    def has_perms(self, perm_list, obj=None):
                        return all(self.has_perm(perm, obj) for perm in perm_list)
                    
                    def has_module_perms(self, app_label):
                        return self.is_superuser
                    
                    def get_username(self):
                        return self.username
                    
                    def save(self, *args, **kwargs):
                        # No-op save for Django auth compatibility
                        pass
                    
                    def delete(self, *args, **kwargs):
                        # No-op delete for Django auth compatibility
                        pass
                
                user = AccountUser(
                    account_id=account_id,
                    username=db_username,
                    is_active=is_active,
                    is_staff=db_username == 'quan_ly',
                    is_superuser=db_username == 'quan_ly'
                )
                return user
        
        return None

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_superuser

    def has_module_perms(self, app_label):
        return True

