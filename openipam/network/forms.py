from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from openipam.network.models import AddressType


class AddressTypeAdminForm(forms.ModelForm):

    def clean(self):
        ranges = self.cleaned_data.get('ranges', [])
        pool = self.cleaned_data.get('pool', '')

        if pool and ranges:
            raise ValidationError(_('Address Types cannot have both a pool and a range.'))

        return self.cleaned_data

    class Meta:
        model = AddressType
