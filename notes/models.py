from django.db import models

from django.conf import settings
from django.db.models import UniqueConstraint
from tinymce import models as tinymce_models
from accounts.models import CustomUser


class Notes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = tinymce_models.HTMLField()
    # video 
    link = models.URLField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through="UserLikes", related_name="note_likes")

    objects = models.Manager()

    def add_like(self, user_id):
        user = CustomUser.objects.get(id=user_id)
        like, created = UserLikes.objects.get_or_create(notes=self, users=user)
        if not created and like.value == "Unlike":
            like.value = "Like"
            like.save()
        self.likes.add(user)

    def remove_like(self, user_id):
        user = CustomUser.objects.get(id=user_id)
        like = UserLikes.objects.get(notes=self, users=user)
        if like:
            if like.value == "Like":
                like.value = "Unlike"
                like.save()
            self.likes.remove(user)

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
        UniqueConstraint(fields=["tags_id", "notes_id"], name="unique_tags_notes")


LIKE_CHOICES = (
    ("Like", "Like"),
    ("Unlike", "Unlike"),
    )


class UserLikes(models.Model):
    notes = models.ForeignKey(Notes, on_delete=models.CASCADE)
    users = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8, default="Unlike")

    objects = models.Manager()

    class Meta:
        UniqueConstraint(fields=["notes", "users"], name="unique_notes_users")