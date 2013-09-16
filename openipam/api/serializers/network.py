from rest_framework import serializers
from openipam.network.models import Network


class NetworkSerializer(serializers.ModelSerializer):
    #network = serializers.CharField()

    class Meta:
        model = Network
        fields = ('network', 'name', 'description')
