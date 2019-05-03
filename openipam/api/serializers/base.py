from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django import forms

from rest_framework import serializers

from netaddr import EUI, mac_bare


class MultipleChoiceField(serializers.Field):
    """
    A field that behaves like multiple choice field of Django forms.
    """

    form_field_class = forms.MultipleChoiceField

    def from_native(self, data):
        if isinstance(data, list):
            for item in data:
                if item not in self.choices:
                    raise serializers.ValidationError(
                        "The item you entered is not in the allowed items list."
                    )
            return data
        else:
            raise serializers.ValidationError("Please provide a valid list.")

    def to_native(self, value):
        return value

    def __init__(self, choices=None, *args, **kwargs):
        self.choices = dict(choices)
        super(MultipleChoiceField, self).__init__(*args, **kwargs)


class ListOrItemField(serializers.Field):
    """
    A field whose values are either a value or lists of values described by the given item field.
    The item field can be another field type (e.g., CharField) or a serializer.
    """

    def __init__(self, child, *args, **kwargs):
        super(ListOrItemField, self).__init__(*args, **kwargs)
        self.item_field = child
        self.list_field = serializers.ListField(child=child, *args, **kwargs)

    def to_representation(self, obj):
        if isinstance(obj, list):
            return self.list_field.to_representation(obj)
        return self.item_field.to_representation(obj)

    def to_internal_value(self, data):
        if isinstance(data, list):
            return self.list_field.to_internal_value(data)
        return self.item_field.to_internal_value(data)


class MACAddressField(serializers.CharField):
    default_error_messages = {"invalid": "Enter a valid mac address."}

    def validate(self, value):
        """
        Check to see if the provided value is a valid choice.
        """
        super(MACAddressField, self).validate(value)
        if value:
            try:
                value = EUI(str(value), dialect=mac_bare)
                return
            except (ValueError, TypeError, ValidationError):
                raise ValidationError(self.error_messages["invalid"] % {"value": value})


class IPAddressField(serializers.CharField):
    default_error_messages = {"invalid": "Enter a valid ip address."}

    def __init__(self, **kwargs):
        super(IPAddressField, self).__init__(**kwargs)
        self.validators.append(validate_ipv46_address)
