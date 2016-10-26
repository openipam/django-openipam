from django.core.exceptions import ValidationError

from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from openipam.network.models import Network, Address, DhcpGroup
from openipam.api.views.base import APIPagination
from openipam.api.serializers.network import NetworkSerializer, AddressSerializer, DhcpGroupListSerializer
from openipam.api.filters.network import NetworkFilter
from openipam.api.permissions import IPAMChangeHostPermission, IPAMAPIAdminPermission, IPAMAPIPermission


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
        Gets details for an address.
    """
    queryset = Address.objects.select_related('network').all()
    serializer_class = AddressSerializer


class AddressUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = AddressSerializer
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
        except ValidationError, e:
            error_list = []
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response({'non_field_errors': error_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)



class DhcpGroupList(generics.ListAPIView):
    queryset = DhcpGroup.objects.select_related().prefetch_related('dhcp_options').all()
    serializer_class = DhcpGroupListSerializer
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
