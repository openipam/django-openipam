from rest_framework import serializers

from openipam.network.models import Network, Address, DhcpGroup, Pool
from openipam.hosts.models import Host

class NetworkSerializer(serializers.ModelSerializer):
    #network = serializers.CharField()

    class Meta:
        model = Network
        fields = ('network', 'name', 'description')


class AddressSerializer(serializers.ModelSerializer):
    address = serializers.CharField(read_only=True)
    network = serializers.CharField(source='network.network', required=False)
    pool = serializers.CharField(required=False)
    host = serializers.CharField(source='host.hostname', required=False, allow_blank=True, allow_null=True)
    gateway = serializers.SerializerMethodField()
    changed_by = serializers.ReadOnlyField(source='changed_by.username')
    changed = serializers.ReadOnlyField()

    def get_gateway(self, obj):
        return str(obj.network.gateway.ip)

    def validate_host(self, value):
        if not isinstance(value, Host):
            host = Host.objects.filter(hostname=value.lower()).first()
            if not host:
                raise serializers.ValidationError('The hostname enetered does not exist.  Please first create the host.')
            return host
        return value

    def validate_network(self, value):
        network = Network.objects.filter(network=value).first()
        if not network:
            raise serializers.ValidationError('The network enetered does not exist.  Please first create the network.')
        elif self.instance.address not in network.network:
            raise serializers.ValidationError('The address is not a part of the network entered.  Please enter a network that contains this address.')
        return network

    def validate_pool(self, value):
        if not isinstance(value, Pool):
            if value.isdigit():
                pool = Pool.objects.filter(pk=value).first()
            else:
                pool = Pool.objects.filter(name=value.lower()).first()
            if not pool:
                raise serializers.ValidationError('The pool enetered does not exist.')
            return pool
        return value

    def update(self, instance, validated_data):
        assert False, validated_data
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


class DhcpGroupListSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = DhcpGroup
