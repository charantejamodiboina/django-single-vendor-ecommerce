from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def has_permission(self, request, view):
        return True
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('the email must be set'))
        if not password:
            raise ValueError(_('the password must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('otp', 0)
        extra_fields.setdefault('first_name', 'admin')
        extra_fields.setdefault('last_name', '')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # # Ensure there is no existing superuser
        # if self.filter(is_superuser=True).exists():
        #     raise ValueError('A superuser already exists.')

        return self.create_user(email, password, **extra_fields)
