from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser, Notes
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label='password', strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='password confirmation', strip=False, required=True, max_length=100,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput, label='email')
    password = forms.CharField(widget=forms.PasswordInput, label='password')

    class Meta:
        model = CustomUser
        fields = ('email', 'password',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email", )


class NotesForm(forms.ModelForm):
    title = forms.CharField(label='Title')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    link = forms.CharField(widget=forms.URLInput, required=False)
    is_public = forms.BooleanField(label='Public', help_text='Check the box too let everyone see this Note')
    class Meta:
        model = Notes
        fields = ('title', 'description', 'link', 'is_public')


class TagsForm(forms.Form):
    tag = forms.CharField(max_length=210, label='Tags', required=False, help_text='separate tags using #,'
                                                                                  ' max length of a tag 30 char,'
                                                                                  ' \n example #sql #python')

    def clean_tag(self):
        tags: str = self.cleaned_data['tag']
        if not tags:
            return None
        if tags.count('#') > 10:
            raise ValidationError('Only 10 tags for a note is allowed')
        if (tags.strip())[0] != "#":  # checks if it starts with '#'
            raise ValidationError('Tags should start with #')
        tag_list: list = (tags.strip()).split('#')
        for i in tag_list:
            if len(i) > 30:
                raise ValidationError('one tag should be maximum 30 characters long')
        return tags
