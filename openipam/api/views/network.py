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
from rest_framework.parsers import FormParser, JSONParser

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
    Lease,
    Pool,
    DefaultPool,
    Building,
    BuildingToVlan,
)
from openipam.api.views.base import APIPagination, ListDestroyViewSet
from openipam.api.serializers import network as network_serializers
from openipam.api.filters.network import NetworkFilter, LeaseFilter
from openipam.api.permissions import IPAMAPIAdminPermission, IPAMAPIPermission

from ipaddress import IPv4Network, ip_interface


class IPAMNetwork(APIView):
    @transaction.atomic
    def create_vlan(
        self, vlan_id, building, name, user, networks=None, downstream_ids=None
    ):
        # Create Vlans and Building to Vlans
        abbrev = building.abbreviation.upper()
        vlan_name = f"{abbrev}.{name}"
        vlan, created = Vlan.objects.get_or_create(
            vlan_id=vlan_id, name=vlan_name, defaults={"changed_by": user}
        )
        BuildingToVlan.objects.get_or_create(
            building=building, vlan=vlan, defaults={"changed_by": user}
        )

        if downstream_ids:
            downstream_buildings = Building.objects.filter(number__in=downstream_ids)
            for building in downstream_buildings:
                BuildingToVlan.objects.get_or_create(
                    building=building, vlan=vlan, defaults={"changed_by": user}
                )

        shared_network = None
        if not networks:
            networks = []
        else:
            shared_network, created = SharedNetwork.objects.get_or_create(
                name=vlan_name, defaults={"changed_by": user}
            )

        for network in networks:
            network_to_vlan = NetworkToVlan.objects.filter(network=network).first()
            if network_to_vlan:
                network_to_vlan.vlan = vlan
                network_to_vlan.changed_by = user
                network_to_vlan.save()
            else:
                NetworkToVlan.objects.get_or_create(
                    network=network, vlan=vlan, defaults={"changed_by": user}
                )
            network.name = vlan_name
            network.description = (
                f"{building.name}/{building.abbreviation}/{building.number} {name}"
            )
            if shared_network:
                network.shared_network = shared_network
            else:
                network.shared_network = None
            network.save()

        return vlan

    @transaction.atomic
    def create_network(self, network_str, building, name, user, dhcp_group_name=None):
        network = IPv4Network(network_str, False)
        gateway = network[1]
        abbrev = building.abbreviation.upper()
        network_name = f"{abbrev}.{name}"
        dhcp_group = None
        if dhcp_group_name:
            dhcp_group = DhcpGroup.objects.filter(name=dhcp_group_name).first()
        network, created = Network.objects.get_or_create(
            network=network,
            defaults={
                "name": network_name,
                "gateway": gateway,
                "dhcp_group": dhcp_group,
                "changed_by": user,
            },
        )

        # Create addresses if network was created, otherwise pass.
        if created:
            # Create addresses for captive portal network
            addresses = []
            for address in network.network:
                reserved = False
                if address in (
                    network.gateway,
                    network.network[0],
                    network.network[-1],
                ):
                    reserved = True
                pool = (
                    DefaultPool.objects.get_pool_default(address)
                    if not reserved
                    else None
                )
                addresses.append(
                    # TODO: Need to set pool eventually.
                    Address(
                        address=address,
                        network=network,
                        reserved=reserved,
                        pool=pool,
                        changed_by=user,
                    )
                )
            if addresses:
                Address.objects.bulk_create(addresses)

        return network


class CreateIPAMNetwork(IPAMNetwork):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    parser_classes = [FormParser, JSONParser]

    @transaction.atomic
    def post(self, request, format=None, **kwargs):
        serializer = network_serializers.IPAMNetworkSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({"serializer": serializer})

        building = serializer.data["building"]
        vlan_id = serializer.data["vlan_id"]
        name = serializer.data["name"]
        dhcp_group_name = serializer.data.get("dhcp_group_name", None)
        downstream_ids = serializer.data.get("downstream_ids", None)

        network = self.create_network(
            network_str=serializer.data["network"],
            building=building,
            name=name,
            user=request.user,
            dhcp_group_name=dhcp_group_name,
        )

        # Create Vlans and Building to Vlans
        self.create_vlan(
            vlan_id=vlan_id,
            building=building,
            user=request.user,
            networks=[network],
            name=name,
            downstream_ids=downstream_ids,
        )

        return Response("Ok!")


class ConvertIPAMNetwork(IPAMNetwork):
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)
    parser_classes = [FormParser, JSONParser]

    @transaction.atomic
    def post(self, request, format=None, **kwargs):
        serializer = network_serializers.ConvertIPAMNetworkSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({"serializer": serializer})

        building = serializer.data["building"]
        vlan_nets = request.data["vlan_nets"]

        # Loop and create the vlans
        for net in vlan_nets:
            for address in net["addresses"]:
                self.create_network(
                    network_str=str(ip_interface(address).network),
                    building=building,
                    name=net["name"],
                    user=request.user,
                    dhcp_group_name=net["dhcp_group_name"],
                )
            self.create_vlan(
                vlan_id=net["vlan_id"],
                building=building,
                user=request.user,
                networks=[
                    Network.objects.get(network=str(ip_interface(address).network))
                    for address in net["addresses"]
                ],
                name=net["name"],
            )

        # routable_networks = serializer.data["routable_networks"]
        # non_routable_networks = serializer.data["non_routable_networks"]

        # # Create Vlans and Building to Vlans
        # # Vlan 10 - routable
        # self.create_vlan(
        #     vlan_id="10",
        #     building=building,
        #     user=request.user,
        #     networks=routable_networks,
        #     name="campus_routable",
        # )
        # # Vlan 20 - non-routable
        # self.create_vlan(
        #     vlan_id="20",
        #     building=building,
        #     user=request.user,
        #     networks=non_routable_networks,
        #     name="campus_nonroutable",
        # )

        # # Vlan 30 - captive
        # if serializer.data.get("captive_network", None):
        #     captive_network = self.create_network(
        #         network_str=serializer.data["captive_network"],
        #         building=building,
        #         name="captive",
        #         user=request.user,
        #         dhcp_group_name="restricted",
        #     )
        #     self.create_vlan(
        #         vlan_id="30",
        #         building=building,
        #         user=request.user,
        #         networks=[captive_network],
        #         name="captive",
        #     )

        # # Vlan 39 - captive_housing
        # if serializer.data.get("captive_housing_network", None):
        #     captive_housing_network = self.create_network(
        #         network_str=serializer.data["captive_housing_network"],
        #         building=building,
        #         name="captive_housing",
        #         user=request.user,
        #         dhcp_group_name="restricted",
        #     )
        #     self.create_vlan(
        #         vlan_id="39",
        #         building=building,
        #         user=request.user,
        #         networks=[captive_housing_network],
        #         name="captive_housing",
        #     )

        # # Vlan 40 - phones
        # if serializer.data.get("phone_network", None):
        #     phone_network = self.create_network(
        #         network_str=serializer.data["phone_network"],
        #         building=building,
        #         name="campus_voice",
        #         user=request.user,
        #         dhcp_group_name="usu_shoretel_phones-untagged",
        #     )
        #     self.create_vlan(
        #         vlan_id="40",
        #         building=building,
        #         user=request.user,
        #         networks=[phone_network],
        #         name="campus_voice",
        #     )

        # # Vlan 90 - management
        # management_network = self.create_network(
        #     network_str=serializer.data["management_network"],
        #     building=building,
        #     name="management",
        #     user=request.user,
        # )
        # self.create_vlan(
        #     vlan_id="90",
        #     building=building,
        #     user=request.user,
        #     networks=[management_network],
        #     name="management",
        # )

        # # Vlan 11 - campus_lab
        # campus_lab_networks = serializer.data.get("campus_lab_networks", [])
        # if campus_lab_networks:
        #     self.update_vlan(
        #         vlan_id="11",
        #         building=building,
        #         user=request.user,
        #         networks=campus_lab_networks,
        #         name="campus_lab",
        #     )

        return Response("Ok!")


class NetworkList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Network.objects.all()
    pagination_class = APIPagination
    serializer_class = network_serializers.NetworkListSerializer
    filter_fields = ("network", "name", "dhcp_group__name")
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
    queryset = NetworkToVlan.objects.select_related(
        "network", "vlan", "changed_by"
    ).all()
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
    queryset = SharedNetwork.objects.select_related("changed_by").all()
    filter_fields = ("id", "name")
    lookup_field = "id"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.SharedNetworkDeleteSerializer
        return network_serializers.SharedNetworkSerializer


class VlanViewSet(viewsets.ModelViewSet):
    queryset = (
        Vlan.objects.select_related("changed_by")
        .prefetch_related("vlan_networks", "buildings")
        .all()
    )
    filter_fields = ("name", "vlan_id", "id")
    lookup_field = "id"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.VlanDeleteSerializer
        return network_serializers.VlanSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.prefetch_related("changed_by", "building_vlans").all()
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


class LeaseViewSet(ListDestroyViewSet):
    queryset = Lease.objects.all()
    filter_class = LeaseFilter
    permission_classes = (IsAuthenticated, IPAMAPIPermission)
    pagination_class = APIPagination

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.LeaseDeleteSerializer
        return network_serializers.LeaseSerializer


class DefaultPoolViewSet(viewsets.ModelViewSet):
    queryset = DefaultPool.objects.all()
    lookup_field = "cidr"
    lookup_value_regex = r"([0-9a-fA-F]{1,4}[\.\:]?){3,4}(\:?\/[0-9]+)?"
    permission_classes = (IsAuthenticated, IPAMAPIAdminPermission)

    def get_serializer_class(self):
        if self.action == "destroy":
            return network_serializers.DefaultPoolDeleteSerializer
        return network_serializers.DefaultPoolSerializer
