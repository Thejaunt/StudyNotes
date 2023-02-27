from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    pass
    # profile_img = models.ImageField()

    def __str__(self):
        return self.username


class Notes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    image = models.ImageField()
    # video 
    link = models.URLField()
    is_publick = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tags(models.Model):
    tag = models.CharField(max_length=80, unique=True)
    note = models.ManyToManyField(Notes, through='NotesTags')



class NotesTags(models.Model):
    tags_id = models.ForeignKey(Notes, on_delete=models.CASCADE)
    notes_id = models.ForeignKey(Tags, on_delete=models.CASCADE)



