"""Serializers for network objects."""

from openipam.network.models import Address, Vlan, Network
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

    class Meta:
        """Meta class for network serializer."""

        model = Network
        fields = "__all__"


class SimpleNetworkSerializer(Field):
    """Network serializer that functions on CIDR format only."""

    def to_representation(self, value):
        """Convert network object to CIDR format."""
        return value.network

    def to_internal_value(self, data):
        """Find network object based on CIDR."""
        network = get_object_or_404(Network, network=data)
        return network


class AddressSerializer(ModelSerializer):
    """Serializer for address objects."""

    network = SimpleNetworkSerializer()
    gateway = SerializerMethodField()
    pool = SerializerMethodField()

    def get_pool(self, obj):
        """Return pool name for network."""
        if obj.pool:
            return {
                "id": obj.pool.id,
                "name": obj.pool.name,
                "description": obj.pool.description,
            }
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
        fields = ("address", "pool", "reserved", "network", "changed", "gateway")


class SimpleAddressSerializer(Field):
    """Address serializer that functions string representation only."""

    def to_representation(self, value):
        """Convert address object to string."""
        return value.address

    def to_internal_value(self, data):
        """Find address object based on string."""
        address = get_object_or_404(Address, address=data)
        return address


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
