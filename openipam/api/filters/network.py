from django_filters import FilterSet, CharFilter
from openipam.network.models import Network


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_type='net_contains_or_equals')
    name = CharFilter(lookup_type='icontains')

    class Meta:
        model = Network
        fields = ['name']
