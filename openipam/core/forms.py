from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from openipam.core.models import FeatureRequest
import autocomplete_light

User = get_user_model()


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class FeatureRequestForm(forms.ModelForm):

    class Meta:
        model = FeatureRequest
        exclude = ('user', 'is_complete',)


class BaseUserObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    user = autocomplete_light.ModelChoiceField('UserAutocomplete')


class BaseGroupObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    group = autocomplete_light.ModelChoiceField('GroupAutocomplete')
