from django_filters import FilterSet, CharFilter
from openipam.network.models import Network, Address


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Network
        fields = ["name", "shared_network"]


class AddressFilter(FilterSet):
    address = CharFilter(lookup_expr="net_contains_or_equals")
    mac = CharFilter(lookup_expr="net_contains_or_equals")

    class Meta:
        model = Address
        fields = ["address", "mac"]
