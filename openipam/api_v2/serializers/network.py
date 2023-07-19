from openipam.network.models import Address, Vlan, Network
from rest_framework.serializers import ModelSerializer
from .users import UserNestedSerializer


class VlanSerializer(ModelSerializer):
    class Meta:
        model = Vlan
        fields = ["id", "vlan_id", "name", "description"]


class NetworkSerializer(ModelSerializer):
    vlan = VlanSerializer()

    class Meta:
        model = Network
        fields = "__all__"


class AddressSerializer(ModelSerializer):
    network = NetworkSerializer()
    changed_by = UserNestedSerializer()

    class Meta:
        model = Address
        fields = (
            "id",
            "address",
            "gateway",
            "pool",
            "reserved",
            "network",
            "changed_by",
            "changed",
        )
