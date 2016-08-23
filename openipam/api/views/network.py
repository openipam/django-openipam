from django.core.exceptions import ValidationError

from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from rest_framework import serializers

from openipam.network.models import Network, Address, DhcpGroup
from openipam.api.views.base import APIPagination
from openipam.api.serializers.network import NetworkSerializer, AddressSerializer, DhcpGroupListSerializer
from openipam.api.filters.network import NetworkFilter


class NetworkList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    pagination_class = APIPagination
    serializer_class = NetworkSerializer
    filter_fields = ('network', 'name',)
    filter_class = NetworkFilter

    def filter_queryset(self, queryset):
        try:
            return super(NetworkList, self).filter_queryset(queryset)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)


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
