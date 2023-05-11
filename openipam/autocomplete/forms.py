from dal import autocomplete
from django import forms

from openipam.hosts.models import (
    Host,
    FreeformAttributeToHost,
    StructuredAttributeValue,
)
from openipam.network.models import Network, AddressType
from openipam.user.models import User
from django.contrib.auth.models import Group


class HostSearchForm(forms.ModelForm):
    pass
