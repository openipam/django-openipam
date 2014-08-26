from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django import forms

from rest_framework import serializers

from netfields.forms import MACAddressFormField

from netaddr import EUI, AddrFormatError, mac_bare


class MultipleChoiceField(serializers.WritableField):
    """
    A field that behaves like multiple choice field of Django forms.
    """
    form_field_class = forms.MultipleChoiceField

    def from_native(self, data):
        if isinstance(data, list):
            for item in data:
                if not item in self.choices:
                    raise serializers.ValidationError("The item you entered is not in the allowed items list.")
            return data
        else:
            raise serializers.ValidationError("Please provide a valid list.")

    def to_native(self, value):
        return value

    def __init__(self, choices=None, *args, **kwargs):
        self.choices = dict(choices)
        super(MultipleChoiceField, self).__init__(*args, **kwargs)


class MACAddressField(serializers.CharField):
    type_name = 'MACAddressField'
    type_label = 'mac_address'
    form_field_class = MACAddressFormField

    default_error_messages = {
        'invalid': 'Enter a valid mac address.',
    }

    def validate(self, value):
        """
        Check to see if the provided value is a valid choice.
        """
        super(MACAddressField, self).validate(value)
        if value:
            try:
                value = EUI(str(value), dialect=mac_bare)
            except (ValueError, TypeError, AddrFormatError):
                raise ValidationError(self.error_messages['invalid'] % {'value': value})


class IPAddressField(serializers.CharField):
    type_name = 'IPAddressField'
    type_label = 'ip_address'
    form_field_class = forms.GenericIPAddressField

    default_error_messages = {
        'invalid': 'Enter a valid ip address.',
    }
    default_validators = [validate_ipv46_address]
