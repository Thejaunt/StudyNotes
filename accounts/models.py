import os
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    def user_dir_path(self, instance=None):
        if instance:
            return os.path.join('Users', str(self.pk), instance)
        return None

    profile_img = models.ImageField(upload_to=user_dir_path, blank=True, null=True, max_length=255)
    name = models.CharField(default="No name", null=True, blank=False, max_length=40)
    email = models.EmailField(_('email address'), unique=True, max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"
