from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django import forms

from openipam.network.models import AddressType, DhcpOptionToDhcpGroup, DhcpGroup, Address

import autocomplete_light
from autocomplete_light.contrib.taggit_field import TaggitField, TaggitWidget

from crispy_forms.helper import FormHelper

from curses.ascii import isprint

import binascii


class AddressAdminForm(forms.ModelForm):
    host = autocomplete_light.ModelChoiceField('HostAutocomplete', required=False)
    network = autocomplete_light.ModelChoiceField('NetworkAutocomplete')

    class Meta:
        model = Address
        exclude = ('changed_by',)


class LeaseAdminForm(forms.ModelForm):
    host = forms.CharField(label='Host Mac')
    address = forms.ModelChoiceField(queryset=Address.objects.all(), widget=forms.TextInput)

    class Meta:
        model = Address
        exclude = ('host',)


class AddressTypeAdminForm(forms.ModelForm):
    def clean(self):
        ranges = self.cleaned_data.get('ranges', [])
        pool = self.cleaned_data.get('pool', '')

        if pool and ranges:
            raise ValidationError(_('Address Types cannot have both a pool and a range.'))

        return self.cleaned_data

    class Meta:
        model = AddressType
        fields = ('name', 'description', 'ranges', 'pool', 'is_default',)


class DhcpOptionToDhcpGroupAdminForm(forms.ModelForm):
    group = autocomplete_light.ModelChoiceField('DhcpGroupAutocomplete')
    readable_value = forms.CharField(label='Value')

    def __init__(self, *args, **kwargs):
        super(DhcpOptionToDhcpGroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance:
            printable = True
            if self.instance.value:
                for c in self.instance.value:
                    if not isprint(c):
                        printable = False
                        break

            if printable:
                self.fields['readable_value'].initial = self.instance.value
            else:
                self.fields['readable_value'].initial = '0x' + binascii.hexlify(self.instance.value)

            self.original_value = self.fields['readable_value'].initial


    def clean_readable_value(self):
        value = self.cleaned_data['readable_value']
        if value[:2] == '0x':
            self.instance.value = binascii.unhexlify(value[2:])
        else:
            self.instance.value = str(value)

        return value

    class Meta:
        model = DhcpOptionToDhcpGroup
        exclude = ('value',)


class NetworkTagForm(forms.Form):
    tags = TaggitField(widget=TaggitWidget('TagAutocomplete'))

    def __init__(self, *args, **kwargs):
        super(NetworkTagForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
