import hashlib

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import connection


class AccountUser:
    """Lightweight user object for records from custom `accounts` table."""

    def __init__(self, account_id, username, is_active, role=None, staff_id=None):
        self.id = account_id
        self.username = username
        self.is_authenticated = True
        self.is_active = bool(is_active)
        self.role = role
        self.staff_id = staff_id
        self.is_staff = role in {'manager', 'admin'}
        self.is_superuser = role in {'manager', 'admin'}
        self.backend = 'apps.core.authentication.CustomAccountBackend'

        class PK:
            def value_to_string(self, obj):
                return str(obj.id)

        class Meta:
            pk = PK()

        self._meta = Meta()

    def get_username(self):
        return self.username

    def has_perm(self, perm=None, obj=None):
        return self.is_superuser

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        # Keep compatibility with auth internals that may call save/delete.
        return None

    def delete(self, *args, **kwargs):
        return None


class CustomAccountBackend(BaseBackend):
    """
    Custom authentication backend for `accounts` table (MD5 hashed passwords).

    This backend gracefully falls back to Django's default user flow when custom
    tables are unavailable (e.g. SQLite test database).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('user')
        if password is None:
            return None

        user_model = get_user_model()

        # First try Django's built-in user.
        try:
            user = user_model.objects.get(username=username)
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            pass

        # Then try custom `accounts` table.
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.id, a.username, a.password_hash, a.is_active, a.is_locked,
                           COALESCE(s.id, NULL) AS staff_id,
                           COALESCE(s.role, NULL) AS role
                    FROM accounts a
                    LEFT JOIN staff s ON s.id = a.staff_id
                    WHERE a.username = %s
                    """,
                    [username],
                )
                row = cursor.fetchone()

                if not row:
                    return None

                account_id, db_username, password_hash, is_active, is_locked, staff_id, role = row

                clean_hash = (
                    password_hash.replace('$md5$', '')
                    if isinstance(password_hash, str) and password_hash.startswith('$md5$')
                    else password_hash
                )
                input_hash = hashlib.md5(password.encode()).hexdigest()

                if not is_locked and clean_hash == input_hash:
                    try:
                        cursor.execute(
                            """
                            UPDATE accounts
                            SET last_login = CURRENT_TIMESTAMP, failed_attempts = 0
                            WHERE id = %s
                            """,
                            [account_id],
                        )
                    except Exception:
                        pass

                    return AccountUser(
                        account_id=account_id,
                        username=db_username,
                        is_active=is_active,
                        role=role,
                        staff_id=staff_id,
                    )

                try:
                    cursor.execute(
                        """
                        UPDATE accounts
                        SET failed_attempts = failed_attempts + 1
                        WHERE id = %s
                        """,
                        [account_id],
                    )
                except Exception:
                    pass

                return None

        except Exception:
            # Common in isolated test DBs where custom tables do not exist.
            return None

    def get_user(self, user_id):
        """Get custom account user by id for session persistence."""
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.id, a.username, a.is_active,
                           COALESCE(s.id, NULL) AS staff_id,
                           COALESCE(s.role, NULL) AS role
                    FROM accounts a
                    LEFT JOIN staff s ON s.id = a.staff_id
                    WHERE a.id = %s
                    """,
                    [user_id],
                )
                row = cursor.fetchone()

                if not row:
                    return None

                account_id, username, is_active, staff_id, role = row
                return AccountUser(
                    account_id=account_id,
                    username=username,
                    is_active=is_active,
                    role=role,
                    staff_id=staff_id,
                )

        except Exception:
            return None

    def has_perm(self, user_obj, perm, obj=None):
        return bool(getattr(user_obj, 'is_superuser', False))

    def has_module_perms(self, app_label):
        return True
