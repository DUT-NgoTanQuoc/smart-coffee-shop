from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import hashlib

class AccountManager(models.Manager):
    """Custom manager for Account"""
    def get_by_natural_key(self, username):
        return self.get(username=username)

class Account(models.Model):
    """
    Custom Account model mapping to existing 'accounts' table
    Unmanaged - table exists from schema.sql
    No PermissionsMixin to avoid reverse accessor clash with Django User
    """
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    role_id = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    failed_attempts = models.SmallIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    class Meta:
        db_table = 'accounts'
        managed = False  # Table exists, no auto migrations
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return self.username

    @classmethod
    def check_password(cls, raw_password):
        """Check MD5 hash from DB"""
        return hashlib.md5(raw_password.encode()).hexdigest() == cls.password_hash.lstrip('$md5$')

    def set_password(self, raw_password):
        """Not used - DB uses MD5"""
        self.password_hash = f'$md5${hashlib.md5(raw_password.encode()).hexdigest()}'

    def check_password_legacy(self, raw_password):
        return hashlib.md5(raw_password.encode()).hexdigest() == self.password_hash.replace('$md5$', '')

