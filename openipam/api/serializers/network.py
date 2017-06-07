from rest_framework import serializers

from openipam.network.models import Network, Address, DhcpGroup, Pool, SharedNetwork, DefaultPool
from openipam.user.models import User
from openipam.hosts.models import Host

from netaddr import EUI, AddrFormatError

from netfields.mac import mac_unix_common
from netfields.rest_framework import InetAddressField, CidrAddressField


class NetworkListSerializer(serializers.ModelSerializer):
    # network = serializers.CharField()

    class Meta:
        model = Network
        fields = ('network', 'name', 'description')

class NetworkCreateUpdateSerializer(serializers.ModelSerializer):
    network = CidrAddressField()
    gateway = InetAddressField(allow_blank=True, allow_null=True)
    dhcp_group = serializers.CharField(allow_blank=True, allow_null=True)
    shared_network = serializers.CharField(allow_blank=True, allow_null=True)

    def validate_dhcp_group(self, value):
        if value:
            dhcp_group_exists = DhcpGroup.objects.filter(name=value).first()
            if not dhcp_group_exists:
                raise serializers.ValidationError('The dhcp group entered does not exist.')
            return dhcp_group_exists
        return None

    def validate_shared_network(self, value):
        if value:
            shared_network_exists = SharedNetwork.objects.filter(name=value).first()
            if not shared_network_exists:
                raise serializers.ValidationError('The shared network entered does not exist.')
            return shared_network_exists
        return None

    def create(self, validated_data):
        validated_data['changed_by'] = self.context['request'].user
        instance = super(NetworkCreateUpdateSerializer, self).create(validated_data)

        network = Network.objects.filter(network=instance.network).first()

        if network:
            addresses = []
            for address in network.network:
                reserved = False
                if address in (network.gateway, network.network[0], network.network[-1]):
                    reserved = True
                pool = DefaultPool.objects.get_pool_default(address) if not reserved else None
                addresses.append(
                    # TODO: Need to set pool eventually.
                    Address(
                        address=address,
                        network=network,
                        reserved=reserved,
                        pool=pool,
                        changed_by=self.context['request'].user,
                    )
                )
            if addresses:
                Address.objects.bulk_create(addresses)

        return instance

    def update(self, instance, validated_data):
        validated_data['changed_by'] = self.context['request'].user
        return super(NetworkCreateUpdateSerializer, self).update(instance, validated_data)

    class Meta:
        model = Network
        exclude = ('changed_by',)

class NetworkDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('network',)
        read_only_fields = ('network',)

class AddressSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)
    network = serializers.CharField()
    pool = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    host = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gateway = serializers.SerializerMethodField()
    changed_by = serializers.ReadOnlyField(source='changed_by.username')
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
                raise serializers.ValidationError('The hostname enetered does not exist.  Please first create the host.')
            return host
        return None

    def validate_network(self, value):
        network = Network.objects.filter(network=value).first()
        if not network:
            raise serializers.ValidationError('The network enetered does not exist.  Please first create the network.')
        elif self.instance.address not in network.network:
            raise serializers.ValidationError('The address is not a part of the network entered.  Please enter a network that contains this address.')
        return network

    def validate_pool(self, value):
        if value and not isinstance(value, Pool):
            if value.isdigit():
                pool = Pool.objects.filter(pk=value).first()
            else:
                pool = Pool.objects.filter(name=value.lower()).first()
            if not pool:
                raise serializers.ValidationError('The pool enetered does not exist.')
            return pool
        return None

    def update(self, instance, validated_data):
        instance.host = validated_data.get('host', instance.host)
        instance.reserved = validated_data.get('reserved', instance.reserved)
        instance.pool = validated_data.get('pool', instance.pool)
        instance.network = validated_data.get('network', instance.network)
        instance.changed_by = self.context['request'].user
        instance.save()
        return instance

    # def save(self):
    #     assert False, self.validated_data
    #     assert False, self.instance.__dict__
    #     # is_new = True if self.instance is None else False
    #     # data = self.validated_data.copy()
    #     # data['instance'] = self.instance
    #     # data['user'] = self.context['request'].user
    #     # self.instance = Host.objects.add_or_update_host(**data)

    #     # LogEntry.objects.log_action(
    #     #     user_id=self.instance.user.pk,
    #     #     content_type_id=ContentType.objects.get_for_model(self.instance).pk,
    #     #     object_id=self.instance.pk,
    #     #     object_repr=force_unicode(self.instance),
    #     #     action_flag=ADDITION if is_new else CHANGE,
    #     #     change_message='API call.'
    #     # )

        return self.instance

    class Meta:
        model = Address
        fields = ('address', 'gateway', 'host', 'pool', 'reserved', 'network', 'changed_by', 'changed',)


class DhcpGroupSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    def create(self, validated_data):
        validated_data['changed_by'] = self.context['request'].user
        instance = super(DhcpGroupSerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data['changed_by'] = self.context['request'].user
        return super(DhcpGroupSerializer, self).update(instance, validated_data)

    class Meta:
        model = DhcpGroup
        fields = '__all__'

class DhcpGroupDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model=DhcpGroup
        fields = ('name',)
        read_only_fields = ('name',)
