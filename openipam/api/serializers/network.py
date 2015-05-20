from rest_framework import serializers
from openipam.network.models import Network, Address, DhcpGroup


class NetworkSerializer(serializers.ModelSerializer):
    #network = serializers.CharField()

    class Meta:
        model = Network
        fields = ('network', 'name', 'description')


class AddressSerializer(serializers.ModelSerializer):
    gateway = serializers.SerializerMethodField()

    def get_gateway(self, obj):
        return str(obj.network.gateway)

    class Meta:
        model = Address
        fields = ('network', 'gateway', 'host', 'reserved', 'changed_by', 'changed',)


class DhcpGroupListSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = DhcpGroup
