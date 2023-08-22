from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions as base_permissions, viewsets, views
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from ..permissions import ReadRestrictObjectPermissions

from ..serializers.network import (
    DhcpGroupSerializer,
    NetworkSerializer,
    AddressSerializer,
    PoolSerializer,
    AddressTypeSerializer,
)
from ..filters.network import NetworkFilter, AddressFilterSet
from .base import APIPagination
from openipam.network.models import Address, DhcpGroup, Network, Pool, AddressType
from netfields import NetManager  # noqa
from ipaddress import ip_address
from guardian.shortcuts import get_objects_for_user


class AddressPagination(APIPagination):
    """Pagination for address views"""

    # I think it makes sense to have address page sizes be powers of 2,
    # since the only way to view a list of addresses is from a network view,
    # and networks are always CIDR blocks, which are powers of 2.
    page_size = 16
    max_page_size = 256


class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
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

    # don't need the action here, use the viewset below


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows any address to be viewed"""

    queryset = Address.objects.all().select_related("host").order_by("address")
    serializer_class = AddressSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = AddressPagination
    filterset_class = AddressFilterSet
    ordering_fields = ["address", "changed"]
    lookup_value_regex = r"(?:(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2}))|(?:[0-9a-fA-F:]+)"


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

    queryset = AddressType.objects.prefetch_related("ranges").all()
    serializer_class = AddressTypeSerializer
