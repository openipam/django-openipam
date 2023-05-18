from rest_framework import serializers
from openipam.hosts.models import (
    FreeformAttributeToHost,
    StructuredAttributeValue,
)
from openipam.network.models import Network, AddressType
from openipam.user.models import User
from django.contrib.auth.models import Group


class AutocompleteSerializer(serializers.Serializer):
    display = serializers.CharField()

    _formatters = {
        FreeformAttributeToHost: lambda x: ["Attribute", x.attribute, x.value],
        StructuredAttributeValue: lambda x: ["Attribute", x.attribute, x.value],
        Network: lambda x: ["Network", x.name, x],
        AddressType: lambda x: ["Address Type", x],
        User: lambda x: ["User", x, x.get_full_name()],
        Group: lambda x: ["Group", x],
    }

    def get_display(self, obj):
        model = obj.__class__

        if model in self._formatters:
            return " | ".join(self._formatters[model](obj))

        return [model.__name__, obj]
