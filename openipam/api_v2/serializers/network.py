"""Serializers for network objects."""

from openipam.api_v2.serializers.base import ChangedBySerializer
from openipam.network.models import Address, DhcpGroup, Vlan, Network, Pool
from rest_framework import serializers as base_serializers
from rest_framework.serializers import ModelSerializer, Field, SerializerMethodField
from .users import UserNestedSerializer
from django.shortcuts import get_object_or_404
import ipaddress


class VlanSerializer(ModelSerializer):
    """Serializer for vlan objects."""

    class Meta:
        """Meta class for vlan serializer."""

        model = Vlan
        fields = ["id", "vlan_id", "name", "description"]


class NetworkSerializer(ModelSerializer):
    """Serializer for network objects."""

    vlans = VlanSerializer(many=True)
    buildings = SerializerMethodField()
    shared_network = SerializerMethodField()
    gateway = SerializerMethodField()
    addresses = SerializerMethodField()

    def get_addresses(self, obj):
        """Return a link to the address listing"""
        return self.context["request"].build_absolute_uri(
            f"/api/v2/networks/{obj.pk}/addresses/"
        )

    def get_gateway(self, obj):
        if obj.gateway:
            return str(obj.gateway.ip)
        else:
            return None

    def get_shared_network(self, obj):
        if obj.shared_network:
            return {
                "id": obj.shared_network.id,
                "name": obj.shared_network.name,
                "description": obj.shared_network.description,
            }
        else:
            return None

    def get_buildings(self, obj):
        # Buildings are linked to vlans, so we need to get the vlans for the network
        # and then get the buildings for those vlans
        buildings = []
        for vlan in obj.vlans.all():
            buildings.extend(
                vlan.buildings.all().values(
                    "id", "name", "abbreviation", "number", "city"
                )
            )
        return buildings

    class Meta:
        """Meta class for network serializer."""

        model = Network
        fields = "__all__"


class SimpleNetworkSerializer(Field):
    """Network serializer that functions on CIDR format only."""

    def to_representation(self, value):
        """Convert network object to CIDR format."""
        return str(value.network)

    def to_internal_value(self, data):
        """Find network object based on CIDR."""
        network = get_object_or_404(Network, network=data)
        return network


class DhcpGroupSerializer(ModelSerializer):
    """Serializer for dhcp group objects."""

    changed_by = ChangedBySerializer()

    class Meta:
        """Meta class for dhcp group serializer."""

        model = DhcpGroup
        fields = "__all__"


class SimpleDhcpGroupSerializer(Field):
    """Dhcp Group serializer that functions on name format only."""

    def to_representation(self, value):
        """Convert dhcp group object to name format."""
        return str(value.name)

    def to_internal_value(self, data):
        """Find dhcp group object based on name."""
        dhcp_group = get_object_or_404(DhcpGroup, name=data)
        return dhcp_group


class PoolSerializer(ModelSerializer):
    """Address pool serializer."""

    dhcp_group = SimpleDhcpGroupSerializer()

    class Meta:
        """Meta class for pool serializer."""

        model = Pool
        fields = "__all__"


class SimpleAddressSerializer(Field):
    """Address serializer that functions string representation only."""

    def to_representation(self, value):
        """Convert address object to string."""
        return str(value)

    def to_internal_value(self, data):
        """Find address object based on string."""
        address = get_object_or_404(Address, address=data)
        return address


class AddressSerializer(ModelSerializer):
    """Serializer for address objects."""

    network = SimpleNetworkSerializer()
    gateway = SerializerMethodField()
    pool = PoolSerializer()
    address = SimpleAddressSerializer()
    host = SerializerMethodField()
    host_name = SerializerMethodField()

    def get_host_name(self, obj):
        """Return host name for address."""
        if obj.host_name:
            return str(obj.host_name)
        else:
            return None

    def get_host(self, obj):
        """Return host name for address."""
        if obj.host_mac:
            return str(obj.host_mac)
        else:
            return None

    def get_gateway(self, obj):
        """Return gateway address for network."""
        return str(obj.network.gateway.ip)

    def validate_network(self, value):
        """Validate that the network contains the address."""
        # get an ip address object from the address field
        address = self.initial_data.get("address")
        if not address:
            raise base_serializers.ValidationError("Address is required.")
        try:
            address = ipaddress.ip_address(address)
        except ValueError:
            raise base_serializers.ValidationError("Invalid IP address.")
        if address not in value.network:
            raise base_serializers.ValidationError("Address is not in network.")
        return value

    class Meta:
        """Meta class for address serializer."""

        model = Address
        fields = (
            "address",
            "pool",
            "reserved",
            "network",
            "changed",
            "gateway",
            "host",
            "host_name",
        )


class LeaseSerializer(ModelSerializer):
    """Serializer for lease objects."""

    address = AddressSerializer()

    class Meta:
        """Meta class for lease serializer."""

        model = Address
        fields = (
            "address",
            "abandoned",
            "server",
            "starts",
            "ends",
        )

        read_only_fields = (
            "address",
            "abandoned",
            "server",
            "starts",
            "ends",
        )
