import binascii

from rest_framework import serializers

from openipam.network.models import (
    Network,
    Address,
    DhcpGroup,
    DhcpOption,
    DhcpOptionToDhcpGroup,
    Pool,
    SharedNetwork,
    DefaultPool,
    Vlan,
    NetworkRange,
    NetworkToVlan,
    Building,
    BuildingToVlan,
)
from openipam.hosts.models import Host
from openipam.api.serializers.base import ChangedBySerializer

from netaddr import EUI, AddrFormatError

from netfields.mac import mac_unix_common
from netfields.rest_framework import InetAddressField, CidrAddressField

from ipaddress import IPv4Network


class RouterUpgradeSerializer(serializers.Serializer):
    routable_networks = serializers.MultipleChoiceField(
        choices=[(network, network) for network in Network.objects.all()]
    )
    non_routable_networks = serializers.MultipleChoiceField(
        choices=[(network, network) for network in Network.objects.all()]
    )
    building = serializers.ChoiceField(
        choices=[
            (building.number, building.number) for building in Building.objects.all()
        ]
    )
    campus_lab_networks = serializers.MultipleChoiceField(
        choices=[(network, network) for network in Network.objects.all()],
        required=False,
    )
    captive_network = serializers.CharField()
    phone_network = serializers.CharField()
    management_network = serializers.CharField()

    def validate_building(self, value):
        building = Building.objects.get(number__iexact=value)
        return building

    def validate_captive_network(self, value):
        try:
            return IPv4Network(value, False)
        except Exception as e:
            raise serializers.ValidationError(e.message)

    validate_phone_network = validate_management_network = validate_captive_network

    # def validate_phone_network(self, value):
    #     try:
    #         return IPv4Network(value, False)
    #     except Exception as e:
    #         raise serializers.ValidationError(e.message)

    # def validate_management_network(self, value):
    #     try:
    #         return IPv4Network(value, False)
    #     except Exception as e:
    #         raise serializers.ValidationError(e.message)


class NetworkVlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlan
        fields = ["id", "vlan_id", "name", "description"]


class NetworkListSerializer(serializers.ModelSerializer):
    vlans = NetworkVlanSerializer(many=True, read_only=True)

    class Meta:
        model = Network
        fields = "__all__"


class NetworkCreateUpdateSerializer(serializers.ModelSerializer):
    network = CidrAddressField()
    gateway = InetAddressField(allow_blank=True, allow_null=True)
    dhcp_group = serializers.CharField(allow_blank=True, allow_null=True)
    shared_network = serializers.CharField(allow_blank=True, allow_null=True)

    def validate_dhcp_group(self, value):
        if value:
            dhcp_group_exists = DhcpGroup.objects.filter(name=value).first()
            if not dhcp_group_exists:
                raise serializers.ValidationError(
                    "The dhcp group entered does not exist."
                )
            return dhcp_group_exists
        return None

    def validate_shared_network(self, value):
        if value:
            shared_network_exists = SharedNetwork.objects.filter(name=value).first()
            if not shared_network_exists:
                raise serializers.ValidationError(
                    "The shared network entered does not exist."
                )
            return shared_network_exists
        return None

    def create(self, validated_data):
        validated_data["changed_by"] = self.context["request"].user
        instance = super(NetworkCreateUpdateSerializer, self).create(validated_data)

        network = Network.objects.filter(network=instance.network).first()

        if network:
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
                        changed_by=self.context["request"].user,
                    )
                )
            if addresses:
                Address.objects.bulk_create(addresses)

        return instance

    def update(self, instance, validated_data):
        validated_data["changed_by"] = self.context["request"].user
        return super(NetworkCreateUpdateSerializer, self).update(
            instance, validated_data
        )

    class Meta:
        model = Network
        exclude = ("changed_by",)


class NetworkDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ("network",)
        read_only_fields = ("network",)


class NetworkRangeSerializer(serializers.ModelSerializer):
    range = CidrAddressField()

    class Meta:
        model = NetworkRange
        fields = ("id", "range")


class NetworkRangeDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkRange
        fields = ("range",)
        read_only_fields = ("range",)


class NetworkToVlanSerializer(ChangedBySerializer):
    network = CidrAddressField()

    def validate_network(self, value):
        if value:
            network_exists = Network.objects.filter(network=value).first()
            if not network_exists:
                raise serializers.ValidationError("The network entered does not exist.")
            return network_exists
        return None

    class Meta:
        model = NetworkToVlan
        fields = "__all__"


class NetworkToVlanDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkToVlan
        fields = ("network", "vlan")
        read_only_fields = ("network", "vlan")


class AddressSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)
    network = serializers.CharField()
    pool = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    host = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gateway = serializers.SerializerMethodField()
    changed_by = serializers.ReadOnlyField(source="changed_by.username")
    changed = serializers.ReadOnlyField()

    def get_gateway(self, obj):
        if obj.network.gateway:
            return str(obj.network.gateway.ip)
        else:
            return None

    def validate_host(self, value):
        if value and not isinstance(value, Host):
            try:
                value = EUI(value, dialect=mac_unix_common)
                host = Host.objects.filter(pk=value).first()
            except (AddrFormatError, TypeError):
                host = Host.objects.filter(hostname=value.lower()).first()
            if not host:
                raise serializers.ValidationError(
                    "The hostname enetered does not exist.  Please first create the host."
                )
            return host
        return None

    def validate_network(self, value):
        network = Network.objects.filter(network=value).first()
        if not network:
            raise serializers.ValidationError(
                "The network enetered does not exist.  Please first create the network."
            )
        elif self.instance.address not in network.network:
            raise serializers.ValidationError(
                "The address is not a part of the network entered.  Please enter a network that contains this address."
            )
        return network

    def validate_pool(self, value):
        if value and not isinstance(value, Pool):
            if value.isdigit():
                pool = Pool.objects.filter(pk=value).first()
            else:
                pool = Pool.objects.filter(name=value.lower()).first()
            if not pool:
                raise serializers.ValidationError("The pool enetered does not exist.")
            return pool
        return None

    def update(self, instance, validated_data):
        instance.host = validated_data.get("host", instance.host)
        instance.reserved = validated_data.get("reserved", instance.reserved)
        instance.pool = validated_data.get("pool", instance.pool)
        instance.network = validated_data.get("network", instance.network)
        instance.changed_by = self.context["request"].user
        instance.save()
        return instance

    class Meta:
        model = Address
        fields = (
            "address",
            "gateway",
            "host",
            "pool",
            "reserved",
            "network",
            "changed_by",
            "changed",
        )


class DhcpGroupSerializer(ChangedBySerializer):
    class Meta:
        model = DhcpGroup
        fields = "__all__"


class DhcpGroupDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DhcpGroup
        fields = ("name",)
        read_only_fields = ("name",)


class DhcpOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DhcpOption
        fields = "__all__"


class DhcpOptionToDhcpGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=DhcpGroup.objects.all()
    )
    option = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=DhcpOption.objects.all()
    )
    readable_value = serializers.CharField(
        source="get_readable_value", read_only=True, label="value"
    )
    value = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    changed_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_group(self, value):
        if value:
            dhcp_group_exists = DhcpGroup.objects.filter(name=value).first()
            if not dhcp_group_exists:
                raise serializers.ValidationError(
                    "The dhcp group entered does not exist."
                )
            return dhcp_group_exists
        return None

    def validate_option(self, value):
        if value:
            dhcp_option_exists = DhcpOption.objects.filter(name=value).first()
            if not dhcp_option_exists:
                raise serializers.ValidationError(
                    "The dhcp option entered does not exist."
                )
            return dhcp_option_exists
        return None

    def validate_value(self, value):
        if value:
            try:
                int(value, 16)
            except ValueError:
                raise serializers.ValidationError(
                    "Value entered was not in hexidecimal."
                )
            return binascii.unhexlify(value)
        return None

    class Meta:
        model = DhcpOptionToDhcpGroup
        fields = ("id", "group", "option", "readable_value", "value", "changed_by")


class DhcpOptionToDhcpGroupDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DhcpOptionToDhcpGroup
        fields = ("group", "option", "value")
        read_only_fields = ("group", "option", "value")


class SharedNetworkSerializer(ChangedBySerializer):
    class Meta:
        model = SharedNetwork
        fields = "__all__"


class SharedNetworkDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedNetwork
        fields = ("name",)
        read_only_fields = ("name",)


class VlanBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "number", "abbreviation", "name"]


class VlanNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ["network", "name", "gateway", "dhcp_group", "shared_network"]


class VlanSerializer(ChangedBySerializer):
    buildings = VlanBuildingSerializer(many=True, read_only=True)
    vlan_networks = VlanNetworkSerializer(many=True, read_only=True)

    class Meta:
        model = Vlan
        fields = "__all__"


class VlanDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlan
        fields = ("name",)
        read_only_fields = ("name",)


class BuildingVlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlan
        fields = ["id", "vlan_id", "name", "description"]


class BuildingSerializer(ChangedBySerializer):
    building_vlans = BuildingVlanSerializer(many=True, read_only=True)

    class Meta:
        model = Building
        fields = "__all__"


class BuildingDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ("name",)
        read_only_fields = ("name",)


class BuildingToVlanSerializer(ChangedBySerializer):
    vlan_id = serializers.SerializerMethodField()

    def get_vlan_id(self, obj):
        return obj.vlan_id

    class Meta:
        model = BuildingToVlan
        fields = "__all__"


class BuildingToVlanDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingToVlan
        fields = ("building", "vlan")
        read_only_fields = ("building", "vlan")


class PoolSerializer(serializers.ModelSerializer):
    name = serializers.SlugField()
    dhcp_group = serializers.CharField(allow_blank=True, allow_null=True)

    def validate_dhcp_group(self, value):
        if value:
            dhcp_group_exists = DhcpGroup.objects.filter(name=value).first()
            if not dhcp_group_exists:
                raise serializers.ValidationError(
                    "The dhcp group entered does not exist."
                )
            return dhcp_group_exists
        return None

    class Meta:
        model = Pool
        fields = "__all__"


class PoolDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ("name",)
        read_only_fields = ("name",)


class DefaultPoolSerializer(serializers.ModelSerializer):
    pool = serializers.CharField(allow_blank=True, allow_null=True)
    cidr = CidrAddressField()

    def validate_pool(self, value):
        if value:
            pool_exists = Pool.objects.filter(cidr=value).first()
            if not pool_exists:
                raise serializers.ValidationError("The pool entered does not exist.")
            return pool_exists
        return None

    class Meta:
        model = DefaultPool
        fields = "__all__"


class DefaultPoolDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultPool
        fields = ("cidr", "pool")
        read_only_fields = ("cidr", "pool")
