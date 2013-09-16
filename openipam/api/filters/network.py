from django_filters import FilterSet, CharFilter
from openipam.network.models import Network, Address, DhcpGroup


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_type='net_contained_or_equal')
    name = CharFilter(lookup_type='icontains')

    class Meta:
        model = Network
        fields = ['network', 'name']
