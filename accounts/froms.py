import imghdr
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, PasswordResetForm, \
    AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label="password", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="password confirmation", strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={"class": "form-control"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = get_user_model()
        fields = ("email", "name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password1"))
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput, label="email")
    password = forms.CharField(widget=forms.PasswordInput, label="password")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("email",)


class ProfileUsernameForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("name",)


class ProfileImageForm(forms.ModelForm):
    profile_img = forms.ImageField()

    class Meta:
        model = get_user_model()
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


class PasswordSetForm(SetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = get_user_model()
        fields = ("new_password1", "new_password2",)


class PassResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput, label="email")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = get_user_model()