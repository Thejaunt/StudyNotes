from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser, Notes, Tags
from django.core.exceptions import ValidationError
import imghdr


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label="password", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="password confirmation", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="username", required=False, max_length=40)

    class Meta:
        model = CustomUser
        fields = ("email", "username",)

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
    is_public = forms.BooleanField(label="Public",
                                   help_text="Check the box too let everyone see this Note", required=False)

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


class ProfileImageForm(forms.ModelForm):
    profile_img = forms.ImageField()

    class Meta:
        model = CustomUser
        fields = ("profile_img",)

    def clean_profile_img(self):
        image_types = {'jpeg': 'image/jpeg',
                       'jpg': 'image/jpeg',
                       'png': 'image/png',
                       }
        img_max_size = 1048576  # about 1Mb
        img = self.cleaned_data.get("profile_img")
        if img is None:
            return img

        if img.size > img_max_size:
            raise ValidationError("The file is too big.")

        img_extension = img.name.split('.')[-1]
        if not img_extension or img_extension.lower() not in image_types.keys():
            raise ValidationError("Wrong extension of the image")

        mime_type = imghdr.what(img)
        if mime_type not in image_types.keys():
            raise ValidationError("Wrong mime-type of the image")

        return img
