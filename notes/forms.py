from django import forms
from .models import Notes, Tags
from django.core.exceptions import ValidationError


class NotesForm(forms.ModelForm):
    title = forms.CharField(label="Title")
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

