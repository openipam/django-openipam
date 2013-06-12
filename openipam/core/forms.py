from django import forms
from django.contrib.auth.models import User as AuthUser
from openipam.core.models import FeatureRequest


class ProfileForm(forms.ModelForm):

    class Meta:
        model = AuthUser
        fields = ('first_name', 'last_name', 'email')


class FeatureRequestAdminForm(forms.ModelForm):

    class Meta:
        model = FeatureRequest
        exclude = ('user',)
