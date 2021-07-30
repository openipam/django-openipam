from django_filters import FilterSet, CharFilter
from openipam.network.models import Network, Lease


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Network
        fields = ["name", "shared_network"]


class LeaseFilter(FilterSet):
    address = CharFilter(field_name="pk")
    host = CharFilter(field_name="host_id")
    ip = CharFilter(field_name="pk")
    mac = CharFilter(field_name="host_id")

    model = Lease
    fields = ["address", "host"]
