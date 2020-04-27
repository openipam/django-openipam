from django import forms
from django.contrib.auth import get_user_model

from openipam.core.models import FeatureRequest, Bookmark

# from dal import autocomplete
from autocomplete_light import shortcuts as al

from urllib.parse import unquote

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class FeatureRequestForm(forms.ModelForm):
    class Meta:
        model = FeatureRequest
        exclude = ("user", "is_complete")


class BookmarkForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_url(self):
        url = self.cleaned_data["url"]
        return unquote(url)

    def save(self, *args, **kwargs):
        bookmark = super(BookmarkForm, self).save(commit=False, *args, **kwargs)
        bookmark.user = self.user
        bookmark.save()
        return bookmark

    class Meta:
        fields = ("url", "title")
        model = Bookmark


class BaseUserObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    # user = forms.ModelChoiceField(
    #     queryset=User.objects.all(),
    #     widget=autocomplete.ModelSelect2(url="user_autocomplete"),
    # )
    user = al.ModelChoiceField("UserAutocomplete")


class BaseGroupObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    # group = forms.ModelChoiceField(
    #     Group.objects.all(), widget=autocomplete.ModelSelect2(url="group_autocomplete")
    # )
    group = al.ModelChoiceField("GroupAutocomplete")
