from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as gl
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # profile_img = models.ImageField()
    email = models.EmailField(gl('email address'), unique=True, max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Notes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    image = models.ImageField()
    # video 
    link = models.URLField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tag = models.CharField(max_length=80, unique=True)
    note = models.ManyToManyField(Notes, through='NotesTags')


class NotesTags(models.Model):
    tags_id = models.ForeignKey(Notes, on_delete=models.CASCADE)
    notes_id = models.ForeignKey(Tags, on_delete=models.CASCADE)



