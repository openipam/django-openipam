from django import forms
from django.contrib.auth import get_user_model
from openipam.core.models import FeatureRequest
from autocomplete_light import shortcuts as al

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class FeatureRequestForm(forms.ModelForm):
    class Meta:
        model = FeatureRequest
        exclude = ("user", "is_complete")


class BaseUserObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    user = al.ModelChoiceField("UserAutocomplete")


class BaseGroupObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    group = al.ModelChoiceField("GroupAutocomplete")
