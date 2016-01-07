from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from openipam.network.models import Network, Address, DhcpGroup, Lease
from openipam.api.views.base import APIPagination
from openipam.api.serializers.network import NetworkSerializer, AddressSerializer, DhcpGroupListSerializer

from django_filters import FilterSet, CharFilter


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_type='net_contained_or_equal')
    name = CharFilter(lookup_type='icontains')

    class Meta:
        model = Network
        fields = ['network', 'name']


class NetworkList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    pagination_class = APIPagination
    serializer_class = NetworkSerializer
    filter_fields = ('network', 'name',)
    filter_class = NetworkFilter


class AddressList(generics.ListAPIView):
    queryset = Address.objects.select_related().all()
    serializer_class = AddressSerializer
    pagination_class = APIPagination
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('address', 'mac',)


class AddressDetail(generics.RetrieveAPIView):
    """
        Gets details for a host.
    """
    queryset = Address.objects.select_related('network').all()
    serializer_class = AddressSerializer


class DhcpGroupList(generics.ListAPIView):
    queryset = DhcpGroup.objects.select_related().prefetch_related('dhcp_options').all()
    serializer_class = DhcpGroupListSerializer
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
