from django_filters import FilterSet, CharFilter
from openipam.network.models import Network


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
    name = CharFilter(lookup_expr="icontains")

    class Meta:
        model = Network
        fields = ["name", "shared_network"]
