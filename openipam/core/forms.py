from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from openipam.core.models import FeatureRequest

from dal import autocomplete

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
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url="user_autocomplete"),
    )


class BaseGroupObjectPermissionForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput)
    group = forms.ModelChoiceField(
        Group.objects.all(), widget=autocomplete.ModelSelect2(url="group_autocomplete")
    )


class MimicUserForm(forms.Form):
    mimic_pk = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="core:autocomplete:user_autocomplete",
            attrs={"data-placeholder": "Mimic User..."},
        ),
    )


class AdvancedSearchForm(forms.Form):
    advanced_search = forms.ChoiceField(
        widget=autocomplete.ListSelect2(
            url="core:autocomplete:ipam_autocomplete",
            attrs={"data-placeholder": "Advanced Search..."},
        ),
    )
