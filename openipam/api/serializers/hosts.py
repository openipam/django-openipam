from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from rest_framework import serializers

from openipam.hosts.models import Host, ExpirationType, Attribute
from openipam.network.models import Network, Address, AddressType, Pool, DhcpGroup
from openipam.api.serializers.base import MACAddressField, IPAddressField

from drf_compound_fields.fields import ListField, ListOrItemField, DictField

from guardian.shortcuts import get_users_with_perms, get_groups_with_perms, get_objects_for_user, assign_perm

from netaddr.core import AddrFormatError

from datetime import timedelta

User = get_user_model()


class HostListSerializer(serializers.ModelSerializer):
    registered_addresses = serializers.SerializerMethodField('get_address')
    leased_addresses = serializers.SerializerMethodField('get_leases')
    is_dynamic = serializers.SerializerMethodField('get_is_dynamic')

    # def get_last_ip_seen(self, obj):
    #     return obj.last_ip_address_seen

    def get_address(self, obj):
        return obj.addresses.all()

    def get_leases(self, obj):
        return obj.leases.all()

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'expires', 'description',
                  'registered_addresses', 'leased_addresses')


class HostDetailSerializer(serializers.ModelSerializer):
    owners = serializers.SerializerMethodField('get_owners')
    registered_addresses = serializers.SerializerMethodField('get_address')
    leased_addresses = serializers.SerializerMethodField('get_leases')
    #last_ip_address_seen = serializers.SerializerMethodField('get_last_ip_seen')
    address_type = serializers.SerializerMethodField('get_address_type')
    is_dynamic = serializers.SerializerMethodField('get_is_dynamic')

    def get_owners(self, obj):
        return obj.get_owners(ids_only=False)

    # def get_last_ip_seen(self, obj):
    #     return obj.last_ip_address_seen

    def get_address(self, obj):
        return obj.addresses.all()

    def get_leases(self, obj):
        return obj.leases.all()

    def get_address_type(self, obj):
        return obj.address_type

    def get_is_dynamic(self, obj):
        return obj.is_dynamic

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'address_type', 'expires', 'is_dynamic', 'description', 'owners',
                  'registered_addresses', 'leased_addresses',)


class HostCreateUpdateSerializer(serializers.Serializer):
    mac = MACAddressField(label='MAC Address', required=False)
    hostname = serializers.CharField(required=False)
    expire_days = serializers.ChoiceField(required=False)
    description = serializers.CharField(required=False)
    #address_type = serializers.ChoiceField(required=False)
    network = serializers.ChoiceField(required=False)
    pool = serializers.ChoiceField(required=False)
    ip_addresses = ListField(IPAddressField(required=False))
    dhcp_group = serializers.ChoiceField(required=False)
    #user_owners = ListField(serializers.CharField(), required=False)
    #group_owners = ListField(serializers.CharField(), required=False)

    def __init__(self, *args, **kwargs):
        super(HostCreateUpdateSerializer, self).__init__(*args, **kwargs)

        self.fields['expire_days'].choices = [(expire.expiration.days, expire.expiration.days) for expire in ExpirationType.objects.all()]
        self.fields['network'].choices = [(network.network, network.network) for network in Network.objects.all()]
        self.fields['pool'].choices = [(pool.name, pool.description) for pool in Pool.objects.all()]
        self.fields['dhcp_group'].choices = [(dhcp_group.pk, dhcp_group.name) for dhcp_group in DhcpGroup.objects.all()]

        if not self.object:
            self.fields['mac'].required = True
            self.fields['hostname'].required = True
            self.fields['expire_days'].required = True

    def restore_object(self, attrs, instance=None):
        if not instance:
            instance = Host()

        # Set mac address
        instance.set_mac_address(attrs.get('mac', instance.mac))

        instance.user = instance.changed_by = self.context['request'].user

        instance.hostname = attrs.get('hostname', instance.hostname)
        instance.description = attrs.get('description', instance.description)

        if attrs.get('expire_days'):
            instance.expire_days = attrs['expire_days']
            instance.exipires = instance.set_expiration(timedelta(int(attrs.get('expire_days'))))

        if attrs.get('dhcp_group'):
            instance.dhcp_group = DhcpGroup.objects.get(pk=attrs['dhcp_group'])

        if attrs.get('pool'):
            instance.pool = Pool.objects.get(slug=attrs['pool'])

        if attrs.get('ip_addresses'):
            instance.ip_addresses = attrs['ip_addresses']

        if attrs.get('network'):
            instance.network = attrs['network']

        return instance

    def save(self, **kwargs):
        instance = super(HostCreateUpdateSerializer, self).save(**kwargs)

        if instance.pool or instance.network or instance.ip_addresses:
            instance.set_network_ip_or_pool()

            # Set address type and re-save
            instance.address_type_id = instance.address_type
            instance.save()

    def validate(self, attrs):

        if not self.object and not attrs.get('ip_address') and not attrs.get('network') and not attrs.get('pool'):
            raise serializers.ValidationError('An IP Address, Network, or Pool is required.')
        net_fields = set(['ip_address', 'network', 'pool'])
        attr_fields = set([key if value else None for key, value in attrs.items()])
        if len(net_fields.intersection(attr_fields)) > 1:
            raise serializers.ValidationError('Only one of IP Address, Network, or Pool is required.')

        return attrs

    def validate_mac(self, attrs, source):
        mac = attrs.get(source)
        host_exists = Host.objects.filter(mac=mac)
        if self.object:
            host_exists = host_exists.exclude(mac=self.object.pk)

        if host_exists:
            if host_exists[0].is_expired:
                host_exists[0].delete()
            else:
                raise serializers.ValidationError('The mac address entered already exists for host: %s.' % host_exists[0].hostname)
        return attrs

    def validate_hostname(self, attrs, source):
        hostname = attrs.get(source)

        host_exists = Host.objects.filter(hostname=hostname)
        if self.object:
            host_exists = host_exists.exclude(hostname=self.object.hostname)

        if host_exists:
            if host_exists[0].is_expired:
                host_exists[0].delete()
            else:
                raise serializers.ValidationError('The hostname entered already exists for host %s.' % host_exists[0].mac)
        return attrs

    def validate_pool(self, attrs, source):
        pool = attrs.get(source)

        if pool:
            user_pools = get_objects_for_user(
                self.context['request'].user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            if pool not in [pool.slug for pool in user_pools]:
                raise serializers.ValidationError('The pool entered is invalid or not permitted.')

        return attrs

    def validate_network(self, attrs, source):
        network = attrs.get(source)

        if network:
            try:
                network = Network.objects.get(network=network)
            except Network.DoesNotExist:
                raise serializers.ValidationError('Please enter a valid network.')
            except AddrFormatError:
                raise serializers.ValidationError('Please enter a valid network.')

            user_pools = get_objects_for_user(
                self.context['request'].user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True),
                network=network,
                host__isnull=True,
                reserved=False,
            ).order_by('address')

            if not address:
                raise serializers.ValidationError('There is no addresses available from this network.'
                                      'Please contact an IPAM Administrator.')
        return attrs

    def validate_ip_addresses(self, attrs, source):
        ip_addresses = attrs.get(source)

        for ip_address in ip_addresses:
            user_pools = get_objects_for_user(
                self.context['request'].user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )
            user_nets = get_objects_for_user(
                self.context['request'].user,
                ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
                any_perm=True
            )

            address = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                address=ip_address,
                host__isnull=True,
                reserved=False
            )
            is_available = True if address else False
            if not is_available:
                raise serializers.ValidationError('The IP Address is reserved, in use, or not allowed.')
        return attrs


class HostOwnerSerializer(serializers.Serializer):
    users = ListField(serializers.CharField(), required=False)
    groups = ListField(serializers.CharField(), required=False)

    def __init__(self, *args, **kwargs):
        super(HostOwnerSerializer, self).__init__(*args, **kwargs)

        if self.object:
            owners = self.object.get_owners(ids_only=False)
            self.object.users = owners[0]
            self.object.groups = owners[1]

    def validate(self, attrs):
        if not attrs['users'] and not attrs['group']:
            raise serializers.ValidationError('A User or Group is required.')

        return attrs


class HostUpdateAttributeSerializer(serializers.Serializer):
    attributes = DictField(serializers.CharField())

    def validate_attributes(self, attrs, source):
        attributes = attrs.get(source)

        for key, attr in attributes.items():
            attr_exists = Attribute.objects.filter(name=key)
            if not attr_exists:
                raise serializers.ValidationError("The attribute '%s', does not exist.  "
                    "Please specifiy a valid attribute key." % key
                )
            else:
                if attr_exists[0].structured:
                    choices = [choice.value for choice in attr_exists[0].choices.all()]
                    if attr not in choices:
                        raise serializers.ValidationError(
                            "The value '%s' for attribute '%s' is not a valid choice.  "
                            "Please specifiy a one of '%s'." % (attr, key, ','.join(choices))
                        )
        return attrs


class HostDeleteAttributeSerializer(serializers.Serializer):
    attributes = ListField(serializers.CharField())

    def validate_attributes(self, attrs, source):
        attributes = attrs.get(source)

        for key in attributes:
            attr_exists = Attribute.objects.filter(name=key)
            if not attr_exists:
                raise serializers.ValidationError("The attribute '%s', does not exist.  "
                    "Please specifiy a valid attribute key." % key
                )
        return attrs

