from django.core.exceptions import ValidationError

from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from openipam.network.models import Network, Address, DhcpGroup, DhcpOption, DhcpOptionToDhcpGroup, SharedNetwork, Vlan, NetworkRange, NetworkToVlan, Pool, DefaultPool, Lease
from openipam.api.views.base import APIPagination
from openipam.api.serializers import network as network_serializers
from openipam.api.filters.network import NetworkFilter
from openipam.api.permissions import IPAMChangeHostPermission, IPAMAPIAdminPermission, IPAMAPIPermission


class NetworkList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    pagination_class = APIPagination
    serializer_class = network_serializers.NetworkListSerializer
    filter_fields = ('network', 'name',)
    filter_class = NetworkFilter

    def filter_queryset(self, queryset):
        try:
            return super(NetworkList, self).filter_queryset(queryset)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

class NetworkDetail(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    serializer_class = network_serializers.NetworkListSerializer

class NetworkCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.NetworkCreateUpdateSerializer
    queryset = Network.objects.all()

class NetworkUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.NetworkCreateUpdateSerializer
    queryset = Network.objects.all()

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValidationError as e:
            error_list = []
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class NetworkDelete(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.NetworkDeleteSerializer
    queryset = Network.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class NetworkRangeViewSet(viewsets.ModelViewSet):
    queryset = NetworkRange.objects.all()
    lookup_field = 'range'
    lookup_value_regex = r'([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.NetworkRangeDeleteSerializer
        return network_serializers.NetworkRangeSerializer

class NetworkToVlanViewSet(viewsets.ModelViewSet):
    queryset = NetworkToVlan.objects.all()
    lookup_field = 'network'
    lookup_value_regex = r'([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.NetworkToVlanDeleteSerializer
        return network_serializers.NetworkToVlanSerializer

class AddressList(generics.ListAPIView):
    queryset = Address.objects.select_related().all()
    serializer_class = network_serializers.AddressSerializer
    pagination_class = APIPagination
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('address', 'mac',)


class AddressDetail(generics.RetrieveAPIView):
    """
        Gets details for an address.
    """
    queryset = Address.objects.select_related('network').all()
    serializer_class = network_serializers.AddressSerializer


class AddressUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.AddressSerializer
    queryset = Address.objects.all()

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        #partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValidationError as e:
            error_list = []
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)



class DhcpGroupViewSet(viewsets.ModelViewSet):
    queryset = DhcpGroup.objects.select_related().prefetch_related('dhcp_options').all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
    lookup_field = 'name'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.DhcpGroupDeleteSerializer
        return network_serializers.DhcpGroupSerializer

class DhcpOptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DhcpOption.objects.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('option',)
    lookup_field = 'option'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.DhcpOptionSerializer

class DhcpOptionToDhcpGroupViewSet(viewsets.ModelViewSet):
    queryset = DhcpOptionToDhcpGroup.objects.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.DhcpOptionToDhcpGroupDeleteSerializer
        return network_serializers.DhcpOptionToDhcpGroupSerializer

class SharedNetworkViewSet(viewsets.ModelViewSet):
    queryset = SharedNetwork.objects.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
    lookup_field = 'name'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.SharedNetworkDeleteSerializer
        return network_serializers.SharedNetworkSerializer

class VlanViewSet(viewsets.ModelViewSet):
    queryset = Vlan.objects.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
    lookup_field = 'name'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.VlanDeleteSerializer
        return network_serializers.VlanSerializer

class PoolViewSet(viewsets.ModelViewSet):
    queryset = Pool.objects.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
    lookup_field = 'name'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.PoolDeleteSerializer
        return network_serializers.PoolSerializer

class DefaultPoolViewSet(viewsets.ModelViewSet):
    queryset = DefaultPool.objects.all()
    lookup_field = 'cidr'
    lookup_value_regex = r'([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?'
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == 'destroy':
            return network_serializers.DefaultPoolDeleteSerializer
        return network_serializers.DefaultPoolSerializer
