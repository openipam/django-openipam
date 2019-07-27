from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import generics
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView

from openipam.network.models import (
    Network,
    Address,
    DhcpGroup,
    DhcpOption,
    DhcpOptionToDhcpGroup,
    SharedNetwork,
    Vlan,
    NetworkRange,
    NetworkToVlan,
    Pool,
    DefaultPool,
    Building,
    BuildingToVlan,
)
from openipam.api.views.base import APIPagination
from openipam.api.serializers import network as network_serializers
from openipam.api.filters.network import NetworkFilter
from openipam.api.permissions import IPAMAPIAdminPermission

from ipaddress import IPv4Network


class RouterUpgrade(APIView):

    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    @transaction.atomic
    def post(self, request, format=None, **kwargs):
        building_number = request.POST.get("building_number")
        routable_networks = request.POST.getlist("routable_networks")
        non_routable_networks = request.POST.getlist("non_routable_networks")
        captive_network = request.POST.get("captive_network")

        building = Building.objects.get(number=building_number)
        routable_networks = Network.objects.filter(network__in=routable_networks)
        non_routable_networks = Network.objects.filter(
            network__in=non_routable_networks
        )

        # Create Vlans and Building to Vlans
        vlan10, created = Vlan.objects.get_or_create(
            vlan_id="10",
            name="%s.campus_routable" % building.abbreviation.upper(),
            changed_by=request.user,
        )
        BuildingToVlan.objects.get_or_create(
            building=building, vlan=vlan10, changed_by=request.user
        )
        vlan20, created = Vlan.objects.get_or_create(
            vlan_id="20",
            name="%s.campus_nonroutable" % building.abbreviation.upper(),
            changed_by=request.user,
        )
        BuildingToVlan.objects.get_or_create(
            building=building, vlan=vlan20, changed_by=request.user
        )
        vlan30, created = Vlan.objects.get_or_create(
            vlan_id="30",
            name="%s.captive" % building.abbreviation.upper(),
            changed_by=request.user,
        )
        BuildingToVlan.objects.get_or_create(
            building=building, vlan=vlan30, changed_by=request.user
        )

        # Create captive portal network
        captive_network = IPv4Network(captive_network)
        captive_gateway = captive_network[1]
        captive_network, created = Network.objects.get_or_create(
            network=captive_network,
            name="%s.captive" % building.abbreviation,
            gateway=captive_gateway,
            dhcp_group=DhcpGroup.objects.get(name="restricted"),
            changed_by=request.user,
        )

        # Create addresses for captive portal network
        captive_addresses = []
        for address in captive_network.network:
            reserved = False
            if address in (
                captive_network.gateway,
                captive_network.network[0],
                captive_network.network[-1],
            ):
                reserved = True
            pool = (
                DefaultPool.objects.get_pool_default(address) if not reserved else None
            )
            captive_addresses.append(
                # TODO: Need to set pool eventually.
                Address(
                    address=address,
                    network=captive_network,
                    reserved=reserved,
                    pool=pool,
                    changed_by=request.user,
                )
            )
        if captive_addresses:
            Address.objects.bulk_create(captive_addresses)

        # Update Network to Vlans
        # Update routables
        for network in routable_networks:
            NetworkToVlan.objects.get_or_create(
                network=network, vlan=vlan10, changed_by=request.user
            )
        for network in non_routable_networks:
            NetworkToVlan.objects.get_or_create(
                network=network, vlan=vlan20, changed_by=request.user
            )

        return Response("Ok!")


class NetworkList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    pagination_class = APIPagination
    serializer_class = network_serializers.NetworkListSerializer
    filter_fields = ("network", "name")
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
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValidationError as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class NetworkDelete(generics.RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.NetworkDeleteSerializer
    queryset = Network.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class NetworkRangeViewSet(viewsets.ModelViewSet):
    queryset = NetworkRange.objects.all()
    lookup_field = "range"
    lookup_value_regex = r"([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.NetworkRangeDeleteSerializer
        return network_serializers.NetworkRangeSerializer


class NetworkToVlanViewSet(viewsets.ModelViewSet):
    queryset = NetworkToVlan.objects.all()
    lookup_field = "network"
    lookup_value_regex = r"([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.NetworkToVlanDeleteSerializer
        return network_serializers.NetworkToVlanSerializer


class AddressList(generics.ListAPIView):
    queryset = Address.objects.select_related().all()
    serializer_class = network_serializers.AddressSerializer
    pagination_class = APIPagination
    filter_fields = ("address", "mac")


class AddressDetail(generics.RetrieveAPIView):
    """
        Gets details for an address.
    """

    queryset = Address.objects.select_related("network").all()
    serializer_class = network_serializers.AddressSerializer


class AddressUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.AddressSerializer
    queryset = Address.objects.all()

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except ValidationError as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class DhcpGroupViewSet(viewsets.ModelViewSet):
    queryset = DhcpGroup.objects.select_related().prefetch_related("dhcp_options").all()
    filter_fields = ("name",)
    lookup_field = "name"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.DhcpGroupDeleteSerializer
        return network_serializers.DhcpGroupSerializer


class DhcpOptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DhcpOption.objects.all()
    filter_fields = ("option",)
    lookup_field = "option"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    serializer_class = network_serializers.DhcpOptionSerializer


class DhcpOptionToDhcpGroupViewSet(viewsets.ModelViewSet):
    queryset = DhcpOptionToDhcpGroup.objects.all()
    filter_fields = ("group__name", "option__name")
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.DhcpOptionToDhcpGroupDeleteSerializer
        return network_serializers.DhcpOptionToDhcpGroupSerializer


class SharedNetworkViewSet(viewsets.ModelViewSet):
    queryset = SharedNetwork.objects.all()
    filter_fields = ("id", "name")
    lookup_field = "id"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.SharedNetworkDeleteSerializer
        return network_serializers.SharedNetworkSerializer


class VlanViewSet(viewsets.ModelViewSet):
    queryset = Vlan.objects.all()
    filter_fields = ("name", "vlan_id", "id")
    lookup_field = "id"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.VlanDeleteSerializer
        return network_serializers.VlanSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.select_related("changed_by").all()
    filter_fields = ("number", "abbreviation")
    lookup_field = "number"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.BuildingDeleteSerializer
        return network_serializers.BuildingSerializer


class BuildingToVlanViewSet(viewsets.ModelViewSet):
    queryset = BuildingToVlan.objects.select_related(
        "building", "vlan", "changed_by"
    ).all()
    filter_fields = ("vlan__id", "vlan__vlan_id", "building__number")
    lookup_field = "pk"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.BuildingToVlanDeleteSerializer
        return network_serializers.BuildingToVlanSerializer


class PoolViewSet(viewsets.ModelViewSet):
    queryset = Pool.objects.all()
    filter_fields = ("name",)
    lookup_field = "name"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.PoolDeleteSerializer
        return network_serializers.PoolSerializer


class DefaultPoolViewSet(viewsets.ModelViewSet):
    queryset = DefaultPool.objects.all()
    lookup_field = "cidr"
    lookup_value_regex = r"([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.DefaultPoolDeleteSerializer
        return network_serializers.DefaultPoolSerializer
