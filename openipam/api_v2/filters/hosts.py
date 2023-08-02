"""Filters for hosts."""
from django_filters import rest_framework as filters
from openipam.hosts.models import Host
from netfields import MACAddressField


class HostFilter(filters.FilterSet):
    """Filter for hosts."""

    class Meta:
        model = Host
        fields = {
            "mac": ["startswith", "endswith", "icontains", "iexact"],
            "hostname": ["startswith", "endswith", "icontains", "iexact"],
        }

        filter_overrides = {
            MACAddressField: {
                "filter_class": filters.CharFilter,
            }
        }
