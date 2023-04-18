from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import NotesForm, TagsForm
from .models import Tags, Notes, NotesTags
from accounts.models import CustomUser
from accounts.froms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class NotesAdmin(admin.ModelAdmin):
    form = NotesForm
    model = Notes
    list_display = ("title", "description", "link", "is_public", "created_at", "updated_at",)


class TagsAdmin(admin.ModelAdmin):
    form = TagsForm
    model = Tags
    list_display = "__all__"


admin.site.register(CustomUser)
admin.site.register(Tags)
admin.site.register(Notes)
admin.site.register(NotesTags)
