from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as gl


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError(gl('The email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(gl('Superuser should have is_staff=True'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(gl('Superuser should have is_superuser=True'))
        return self.create_user(email, password, **kwargs)
