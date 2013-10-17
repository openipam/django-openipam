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


class FeatureRequestAdminForm(forms.ModelForm):

    class Meta:
        model = FeatureRequest
        exclude = ('user',)


class BaseUserObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    user = forms.ModelChoiceField(User.objects.all(),
        widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))


class BaseGroupObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    group = forms.ModelChoiceField(Group.objects.all(),
        widget=autocomplete_light.ChoiceWidget('GroupAutocomplete'))
