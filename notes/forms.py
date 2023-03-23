from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser, Notes, Tags
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label="password", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="password confirmation", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomUser
        fields = ("email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput, label="email")
    password = forms.CharField(widget=forms.PasswordInput, label="password")

    class Meta:
        model = CustomUser
        fields = ("email", "password",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", )


class NotesForm(forms.ModelForm):
    title = forms.CharField(label="Title")
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    link = forms.CharField(widget=forms.URLInput, required=False)
    is_public = forms.BooleanField(label="Public", help_text="Check the box too let everyone see this Note", required=False)

    class Meta:
        model = Notes
        fields = ("title", "description", "link", "is_public")


class TagsForm(forms.Form):
    tag = forms.CharField(max_length=30, label="", required=False)

    class Meta:
        model = Tags
        fields = ("tag",)

    def clean_tag(self):
        tag: str = self.cleaned_data["tag"]
        if not tag:
            return None
        if len(tag) > 30:
            raise ValidationError("one tag should be maximum 30 characters long")
        return " ".join(tag.split()).lower()
