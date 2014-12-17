from rest_framework import serializers
from openipam.network.models import Network, Address


class NetworkSerializer(serializers.ModelSerializer):
    #network = serializers.CharField()

    class Meta:
        model = Network
        fields = ('network', 'name', 'description')


class AddressSerializer(serializers.ModelSerializer):
    gateway = serializers.SerializerMethodField('get_gateway')

    def get_gateway(self, obj):
        return obj.network.gateway

    class Meta:
        model = Address
        fields = ('network', 'gateway', 'host', 'reserved', 'changed_by', 'changed',)
