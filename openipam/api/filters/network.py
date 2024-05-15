from django_filters import FilterSet, CharFilter, IsoDateTimeFilter
from openipam.network.models import Network, Lease, Address


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
    network_in = CharFilter(lookup_expr="net_contained_or_equal", field_name="network")
    name = CharFilter(lookup_expr="icontains")
    dhcp_group = CharFilter(field_name="dhcp_group__name", lookup_expr="icontains")

    class Meta:
        model = Network
        fields = ["name", "shared_network", "dhcp_group__name"]


class LeaseFilter(FilterSet):
    address = CharFilter(field_name="pk")
    host = CharFilter(field_name="host_id")
    ip = CharFilter(field_name="pk")
    mac = CharFilter(field_name="host_id")

    starts_lte = IsoDateTimeFilter(field_name="starts", lookup_expr="lte")
    ends_gte = IsoDateTimeFilter(field_name="ends", lookup_expr="gte")

    class Meta:
        model = Lease
        fields = ["address", "host", "starts", "ends"]


class AddressFilter(FilterSet):
    address = CharFilter(lookup_expr="exact")
    host = CharFilter(lookup_expr="istartswith", field_name="host_id__hostname")
    in_network = CharFilter(lookup_expr="net_contained", field_name="address")

    class Meta:
        model = Address
        fields = ["address", "host", "network"]
