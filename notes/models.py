from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as gl
from .managers import CustomUserManager
from django.db.models import UniqueConstraint
import os


class CustomUser(AbstractBaseUser, PermissionsMixin):
    def user_dir_path(self, instance=None):
        if instance:
            return os.path.join('Users', str(self.pk), instance)
        return None

    profile_img = models.ImageField(upload_to=user_dir_path, blank=True, null=True, max_length=255)
    username = models.CharField(default="No name", null=True, blank=False, max_length=40)
    email = models.EmailField(gl('email address'), unique=True, max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(f"{self.username}: {self.email}")


class Notes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    # video 
    link = models.URLField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class Tags(models.Model):
    tag = models.CharField(max_length=80, unique=True)
    note = models.ManyToManyField(Notes, through='NotesTags')
    objects = models.Manager()

    def __str__(self):
        return self.tag


class NotesTags(models.Model):
    notes_id = models.ForeignKey(Notes, on_delete=models.CASCADE)
    tags_id = models.ForeignKey(Tags, on_delete=models.CASCADE)

    class Meta:
        UniqueConstraint(fields=['tags_id', 'notes_id'], name='unique_tags_notes')
