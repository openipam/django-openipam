from functools import reduce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions as base_permissions, viewsets, views
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from django.db.models import Q

from ..permissions import ReadRestrictObjectPermissions

from ..serializers.network import (
    DhcpGroupSerializer,
    NetworkSerializer,
    SharedNetworkSerializer,
    AddressSerializer,
    PoolSerializer,
    AddressTypeSerializer,
)
from ..filters.network import NetworkFilter, AddressFilterSet
from .base import APIPagination
from openipam.network.models import (
    Address,
    DhcpGroup,
    Network,
    NetworkRange,
    Pool,
    AddressType,
    Lease,
    DefaultPool,
    SharedNetwork,
)
from netfields import NetManager  # noqa
from ipaddress import ip_address
from guardian.shortcuts import get_objects_for_user
from .base import APIModelViewSet


class AddressPagination(APIPagination):
    """Pagination for address views"""

    # I think it makes sense to have address page sizes be powers of 2,
    # since the only way to view a list of addresses is from a network view,
    # and networks are always CIDR blocks, which are powers of 2.
    page_size = 16
    max_page_size = 256


class NetworkViewSet(APIModelViewSet):
    """API endpoint that allows networks to be viewed"""

    # TODO: figure out how to support editing networks. This is a read-only viewset
    # for now.

    queryset = (
        Network.objects.all()
        .prefetch_related("vlans__buildings")
        .select_related("changed_by", "shared_network")
    )
    serializer_class = NetworkSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.DjangoObjectPermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = APIPagination
    filterset_class = NetworkFilter

    # The primary key is the network CIDR, so yay, we get to use regex to parse an IP address
    lookup_value_regex = r"((?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\/(?:3[0-2]|[0-2]?\d))|(?:[0-9a-fA-F:]+\/\d{1,3})"

    ordering_fields = ["network", "name", "changed"]

    def get_queryset(self):
        """Filter out networks that the user does not have read access to."""
        # Don't waste time if the user is an admin
        if self.request.user.is_ipamadmin:
            return self.queryset
        return get_objects_for_user(
            self.request.user,
            [
                "network.add_records_to_network",
                "network.is_owner_network",
                "network.change_network",
            ],
            self.queryset,
            any_perm=True,
        )

    @action(
        detail=False,
        methods=["get"],
        queryset=SharedNetwork.objects.all(),
        serializer_class=SharedNetworkSerializer,
        pagination_class=APIPagination,
        filter_backends=[],
        url_path=r"shared-networks",
        url_name="shared-networks",
    )
    def shared_networks(self, request):
        """Return all shared networks."""
        shared_networks = self.get_queryset()
        paginated = self.paginate_queryset(shared_networks)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        queryset=Address.objects.all()
        .select_related("host", "pool")
        .order_by("address"),
        serializer_class=AddressSerializer,
        filterset_class=AddressFilterSet,
        pagination_class=AddressPagination,
        ordering_fields=["address", "changed"],
        url_name="address-list",
    )
    def addresses(self, request, pk=None):
        """Return all addresses in a given network."""
        network = Network.objects.get(network=pk)
        addresses = self.get_queryset().filter(network=network)
        paginated = self.paginate_queryset(addresses)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        queryset=Address.objects.all().select_related("host", "pool"),
        serializer_class=AddressSerializer,
        filter_backends=[],
        url_path=r"addresses/(?P<address>(?:(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2}))|(?:[0-9a-fA-F:]+))",
        url_name="address-detail",
    )
    def address(self, request, pk=None, address=None):
        """Return a single address in a given network."""
        network = Network.objects.get(network=pk)
        try:
            address = self.get_queryset().select_related("network").get(address=address)
        except Address.DoesNotExist:
            return Response(status=404, data={"detail": "Address not found."})
        if address.network != network:
            network = str(address.network.network)
            return Response(
                status=404,
                data={"detail": f"Address not in this network, try {network} instead."},
            )
        serializer = self.get_serializer(address)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        queryset=Network.objects.all(),
        serializer_class=NetworkSerializer,
        filter_backends=[],
        url_path=r"release-abandoned-leases",
        url_name="release-abandoned-leases",
    )
    def release_abandoned_leases(self, request, pk=None):
        """Release abandoned leases in a given network."""
        network = Network.objects.get(network=pk)
        Lease.objects.filter(
            address__address__net_contained_or_equal=network.network, abandoned=True
        ).update(abandoned=False, host="000000000000")
        return Response(status=200, data={"detail": "Abandoned leases released."})

    @action(
        detail=True,
        methods=["get"],
        queryset=Network.objects.all(),
        serializer_class=NetworkSerializer,
        filter_backends=[],
        url_path=r"tag-network",
        url_name="tag-network",
    )
    def tag_network(self, request, pk=None):
        """Tag a network."""
        network = Network.objects.get(network=pk)
        tags = request.query_params.get("tags", None)
        try:
            tags = tags.split(",")
            network.tags.add(tags)
            network.save()
            return Response(status=200, data={"detail": "Network tagged."})
        except Exception:
            return Response(status=400, data={"detail": "Invalid tags."})

    # resize network
    @action(
        detail=True,
        methods=["get"],
        queryset=Network.objects.all(),
        serializer_class=NetworkSerializer,
        filter_backends=[],
        url_path=r"resize-network",
        url_name="resize-network",
    )
    def resize_network(self, request, pk=None):
        """Resize a network."""
        network = Network.objects.get(network=pk)
        new_network = request.query_params.get("new_network", None)
        if new_network:
            # Update primary key
            Network.objects.filter(network=network).update(network=new_network)
            new_network = Network.objects.filter(network=new_network).first()

            addresses = []
            existing_addresses = [
                address.address
                for address in Address.objects.filter(
                    address__net_contained_or_equal=new_network
                )
            ]

            for address in new_network.network:
                if address not in existing_addresses:
                    reserved = False
                    if address in (
                        new_network.gateway,
                        new_network.network[0],
                        new_network.network[-1],
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
                            network=new_network,
                            reserved=reserved,
                            pool=pool,
                            changed_by=request.user,
                        )
                    )
            if addresses:
                Address.objects.bulk_create(addresses)

            network.save()
            return Response(status=200, data={"detail": "Network resized."})
        else:
            return Response(status=400, data={"detail": "Invalid network."})


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows any address to be viewed"""

    queryset = Address.objects.all().select_related("host").order_by("address")
    serializer_class = AddressSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = AddressPagination
    filterset_class = AddressFilterSet
    ordering_fields = ["address", "changed"]
    lookup_value_regex = r"(?:(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2}))|(?:[0-9a-fA-F:]+)"

    def get_queryset(self):
        """Restrict to only addresses that are a part of networks we are allowed to add records to."""
        # Don't waste time if the user is an admin
        if self.request.user.is_ipamadmin:
            return self.queryset
        allowed_nets = get_objects_for_user(
            self.request.user,
            ["network.add_records_to_network", "network.is_owner_network"],
            Network,
            any_perm=True,
        )
        return self.queryset.filter(network__in=allowed_nets)


class AddressPoolViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows address pools to be viewed"""

    queryset = Pool.objects.all().select_related("dhcp_group", "pool")
    serializer_class = PoolSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    # No need for filters, there are only a few pools
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "changed"]
    pagination_class = APIPagination


class DhcpGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows DHCP groups to be viewed"""

    queryset = DhcpGroup.objects.all()
    serializer_class = DhcpGroupSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "changed"]
    pagination_class = APIPagination


class AddressTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows AddressTypes to be viewed."""

    # Use prefetch_related for ranges, since it's a many-to-many relationship
    # Use select_related for pool, since it's a foreign key
    queryset = (
        AddressType.objects.prefetch_related("ranges").select_related("pool").all()
    )
    serializer_class = AddressTypeSerializer
    permission_classes = [base_permissions.IsAuthenticated]

    def get_queryset(self):
        """Restrict to address types that have a range that the user can add records to."""
        # Don't waste time if the user is an admin
        if self.request.user.is_ipamadmin:
            return self.queryset

        # This is stupid, object-level permissions for address types are not implemented
        # so we need to do this using network and pool permissions. This is slow and hits
        # the database a lot, but it's the only way to do it right now.
        allowed_networks = get_objects_for_user(
            self.request.user,
            ["network.add_records_to_network", "network.is_owner_network"],
            Network,
            any_perm=True,
        ).values_list("network", flat=True)
        allowed_pools = get_objects_for_user(
            self.request.user,
            ["network.add_records_to_pool"],
            Pool,
            any_perm=True,
        )
        query = Q(pk__in=[])
        if allowed_networks:
            query |= reduce(
                lambda x, y: x | y,
                [Q(ranges__range__net_overlaps=net) for net in allowed_networks],
            )
        if allowed_pools:
            query |= reduce(
                lambda x, y: x | y,
                [Q(pool__in=allowed_pools)],
            )

        return self.queryset.filter(query).distinct()
