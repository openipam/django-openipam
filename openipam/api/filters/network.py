from django_filters import FilterSet, CharFilter, IsoDateTimeFilter
from openipam.network.models import Network, Lease


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
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

    starts_gte = IsoDateTimeFilter(field_name="starts", lookup_expr="gte")
    ends_lte = IsoDateTimeFilter(field_name="ends", lookup_expr="lte")

    class Meta:
        model = Lease
        fields = ["address", "host", "starts", "ends"]
