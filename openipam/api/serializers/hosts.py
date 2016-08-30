from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import connection
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.encoding import force_unicode
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from openipam.hosts.models import Host, Attribute, StructuredAttributeValue, Disabled
from openipam.network.models import Network, Address, Pool, DhcpGroup
from openipam.api.serializers.base import MACAddressField, IPAddressField, ListOrItemField

from guardian.shortcuts import get_objects_for_user

User = get_user_model()


class HostMacSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ('mac',)
        read_only_fields = ('mac',)


class HostListSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    disabled_flag = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(HostListSerializer, self).__init__(*args, **kwargs)

        show_attributes = self.context['request'].GET.get('attributes', None)
        if not show_attributes:
            self.fields.pop('attributes')

    def get_addresses(self, obj):
        addresses = {
            'leased': [str(lease.address) for lease in filter(lambda x: x.ends > timezone.now(), obj.leases.all())],
            'registered': [str(address.address) for address in obj.addresses.all()]
        }
        return addresses

    def get_master_ip_address(self, obj):
        return obj.master_ip_address

    def get_attributes(self, obj):
        def dictfetchall(cursor):
            desc = cursor.description
            return [
                dict(zip([col[0] for col in desc], row))
                for row in cursor.fetchall()
            ]

        c = connection.cursor()
        c.execute('''
            SELECT name, value from attributes_to_hosts
                WHERE mac = %s
        ''', [str(obj.mac)])

        rows = dictfetchall(c)
        return rows

    def get_disabled_flag(self, obj):
        disabled_host = getattr(obj, 'disabled_host', False)
        if disabled_host:
            return {
                'status': True,
                'reason': disabled_host.reason,
                'changed_by': disabled_host.changed_by.get_full_name(),
                'changed': disabled_host.changed,
            }
        else:
            return {
                'status': False,
            }

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'expires', 'expire_days', 'addresses', 'master_ip_address',
                  'description', 'is_disabled', 'is_dynamic', 'attributes', 'disabled_flag')


class HostDetailSerializer(serializers.ModelSerializer):
    owners = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    address_type = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    disabled_flag = serializers.SerializerMethodField()

    def get_owners(self, obj):
        users, groups = obj.get_owners(owner_detail=True)
        user_groups = User.objects.filter(groups__in=[group[0] for group in groups])
        users_from_groups = []
        for user in user_groups:
            users_from_groups.append([
                user.pk,
                user.username,
                user.get_full_name(),
                user.email,
                [group.name for group in user.groups.filter(pk__in=[group[0] for group in groups])]
            ])
        owners = {
            'users': users,
            'groups': groups,
            'users_from_groups': users_from_groups
        }
        return owners

    def get_addresses(self, obj):
        addresses = {
            'leased': [str(lease.address) for lease in obj.leases.filter(ends__gt=timezone.now())],
            'registered': [str(address) for address in obj.addresses.all()]
        }
        return addresses

    def get_master_ip_address(self, obj):
        return obj.master_ip_address

    def get_address_type(self, obj):
        return str(obj.address_type)

    def get_attributes(self, obj):
        def dictfetchall(cursor):
            desc = cursor.description
            return [
                dict(zip([col[0] for col in desc], row))
                for row in cursor.fetchall()
            ]

        c = connection.cursor()
        c.execute('''
            SELECT name, value from attributes_to_hosts
                WHERE mac = %s
        ''', [str(obj.mac)])

        rows = dictfetchall(c)
        return rows

    def get_disabled_flag(self, obj):
        disabled_host = getattr(obj, 'disabled_host', False)
        if disabled_host:
            return {
                'status': True,
                'reason': disabled_host.reason,
                'changed_by': disabled_host.changed_by.get_full_name(),
                'changed': disabled_host.changed,
            }
        else:
            return {
                'status': False,
            }

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'address_type', 'expires', 'expire_days', 'is_dynamic', 'description', 'owners',
                  'addresses', 'master_ip_address', 'attributes', 'disabled_flag',)


class HostCreateUpdateSerializer(serializers.ModelSerializer):
    mac = MACAddressField()
    expire_days = serializers.CharField(required=False, allow_blank=True)
    network = serializers.ChoiceField(required=False, allow_blank=True, choices=[])
    pool = serializers.ChoiceField(required=False, allow_blank=True, choices=[])
    ip_address = IPAddressField(required=False, allow_blank=True)
    dhcp_group = serializers.ChoiceField(required=False, allow_blank=True, choices=[])
    user_owners = ListOrItemField(serializers.CharField(required=False), required=False)
    group_owners = ListOrItemField(serializers.CharField(required=False), required=False)

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'expire_days', 'description', 'network', 'pool', 'ip_address', 'dhcp_group', 'user_owners', 'group_owners')

    def __init__(self, *args, **kwargs):
        super(HostCreateUpdateSerializer, self).__init__(*args, **kwargs)

        # THIS IS STUPID!
        blank_choice = [('', '-------------')]
        self.fields['network'] = serializers.ChoiceField(
            required=False,
            choices=blank_choice + [
                (network.network, network.network) for network in Network.objects.all()
            ]
        )
        self.fields['pool'] = serializers.ChoiceField(
            required=False,
            choices=blank_choice + [
                (pool.name, pool.name) for pool in Pool.objects.all()
            ]
        )
        self.fields['dhcp_group'] = serializers.ChoiceField(
            required=False,
            choices=blank_choice + [
                (dhcp_group.name, dhcp_group.name) for dhcp_group in DhcpGroup.objects.all()
            ]
        )

    def to_representation(self, instance):
        ret = super(HostCreateUpdateSerializer, self).to_representation(instance)
        ret['ip_address'] = instance.master_ip_address
        if instance.dhcp_group:
            ret['dhcp_group'] = instance.dhcp_group.name
        return ret

    def save(self):
        is_new = True if self.instance is None else False
        data = self.validated_data.copy()
        data['instance'] = self.instance
        data['user'] = self.context['request'].user
        self.instance = Host.objects.add_or_update_host(**data)

        LogEntry.objects.log_action(
            user_id=self.instance.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.instance).pk,
            object_id=self.instance.pk,
            object_repr=force_unicode(self.instance),
            action_flag=ADDITION if is_new else CHANGE,
            change_message='API call.'
        )

        return self.instance

    def validate(self, data):
        if not self.instance and not data.get('hostname'):
            raise serializers.ValidationError('A Hostname is required.')
        if not self.instance and not data.get('expire_days'):
            raise serializers.ValidationError('Expire days is required.')
        if not self.instance and not data.get('ip_address') and not data.get('network') and not data.get('pool'):
            raise serializers.ValidationError('An IP Address, Network, or Pool is required.')
        net_fields = set(['ip_address', 'network', 'pool'])
        attr_fields = set([key if value else None for key, value in data.items()])
        if len(net_fields.intersection(attr_fields)) > 1:
            raise serializers.ValidationError('Only one of IP Address, Network, or Pool is required.')
        return data

    def validate_mac(self, value):
        mac = value
        mac = ''.join([c for c in mac if c.isdigit() or c.isalpha()])

        if len(mac) != 12:
            raise serializers.ValidationError('The mac address entered is not valid: %s.' % mac)

        host_exists = Host.objects.filter(mac=value)
        if self.instance:
            host_exists = host_exists.exclude(mac=self.instance.pk)

        if host_exists:
            if host_exists[0].is_expired:
                if host_exists[0].is_disabled:
                    raise serializers.ValidationError('The mac address %s cannot be added because it is currently diabled.' % host_exists[0].hostname)
                else:
                    host_exists[0].delete(user=self.context['request'].user)
            else:
                raise serializers.ValidationError('The mac address entered already exists for host: %s.' % host_exists[0].hostname)
        return value

    def validate_hostname(self, value):
        hostname = value
        host_exists = Host.objects.filter(hostname=hostname.lower())
        if self.instance:
            host_exists = host_exists.exclude(hostname=self.instance.hostname)

        if host_exists:
            if host_exists[0].is_expired:
                host_exists[0].delete(user=self.context['request'].user)
            else:
                raise serializers.ValidationError('The hostname entered already exists for host %s.' % host_exists[0].mac)
        return value

    def validate_pool(self, value):
        pool = value

        if pool:
            user_pools = get_objects_for_user(
                self.context['request'].user,
                ['network.add_records_to_pool', 'network.change_pool'],
                any_perm=True
            )

            if pool not in [p.name for p in user_pools]:
                raise serializers.ValidationError('The pool entered is invalid or not permitted.')

        return value

    def validate_network(self, value):
        network = value

        if network:
            try:
                network = Network.objects.get(network=network)
            except (Network.DoesNotExist, ValidationError):
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
        return value

    def validate_ip_address(self, value):
        ip_address = value

        if ip_address:
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

            # Check address that are assigned and free to use
            addresses = Address.objects.filter(
                Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
                Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
                Q(host__isnull=True) | Q(host=self.instance),
                address=ip_address,
                reserved=False
            ).values_list('address', flat=True)

            if ip_address not in addresses:
                raise serializers.ValidationError("The IP Address '%s' is reserved, in use, or not allowed." % ip_address)
        return value


class HostRenewSerializer(serializers.ModelSerializer):
    expire_days = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        instance.expire_days = validated_data.get('expire_days')
        instance.user = self.context['request'].user
        instance.exipires = instance.set_expiration(validated_data.get('expire_days'))
        instance.save(user=instance.user)

        return instance

    class Meta:
        model = Host
        fields = ('expire_days', 'mac', 'hostname')
        read_only_fields = ('mac', 'hostname')


class HostOwnerSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.CharField(), required=False)
    groups = serializers.ListField(child=serializers.CharField(), required=False)

    def __init__(self, *args, **kwargs):
        super(HostOwnerSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            owners = self.instance.get_owners(name_only=True)
            self.instance.users = owners[0]
            self.instance.groups = owners[1]

    def validate(self, data):
        if not data.get('users') and not data.get('groups'):
            raise serializers.ValidationError('A User or Group is required.')

        return data


class HostUpdateAttributeSerializer(serializers.Serializer):
    attributes = serializers.DictField(child=serializers.CharField())

    def validate_attributes(self, value):
        attributes = value

        for key, attr in attributes.items():
            attr_exists = Attribute.objects.filter(name=key)
            if not attr_exists:
                raise serializers.ValidationError("The attribute '%s', does not exist.  "
                    "Please specifiy a valid attribute key." % key)
            else:
                if attr_exists[0].structured:
                    choices = [choice.value for choice in attr_exists[0].choices.all()]
                    if attr not in choices:
                        raise serializers.ValidationError(
                            "The value '%s' for attribute '%s' is not a valid choice.  "
                            "Please specifiy a one of '%s'." % (attr, key, ','.join(choices))
                        )
        return value


class HostDeleteAttributeSerializer(serializers.Serializer):
    attributes = serializers.ListField(child=serializers.CharField())

    def validate_attributes(self, value):
        attributes = value

        for key in attributes:
            attr_exists = Attribute.objects.filter(name=key)
            if not attr_exists:
                raise serializers.ValidationError("The attribute '%s', does not exist.  "
                    "Please specifiy a valid attribute key." % key)
        return value


class AttributeListSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = Attribute


class StructuredAttributeValueListSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField()
    changed_by = serializers.SerializerMethodField()

    def get_attribute(self, obj):
        return obj.attribute.name

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = StructuredAttributeValue


class DisabledHostListUpdateSerializer(serializers.ModelSerializer):
    host = MACAddressField()
    changed_by = serializers.CharField()
    mac = serializers.SerializerMethodField()

    def to_representation(self, obj):
        ret = super(DisabledHostListUpdateSerializer, self).to_representation(obj)
        ret['changed_by'] = '%s (%s)' % (obj.changed_by.get_full_name(), obj.changed_by.username)
        return ret

    def validate_host(self, value):
        try:
            host = Host.objects.filter(mac=value).first()
            if not host:
                raise serializers.ValidationError('No Host found from MAC address entered.')
            disabled_exists = Disabled.objects.filter(pk=value)
            if disabled_exists:
                raise serializers.ValidationError("Host '%s' has already been disabled." % value)
        except ValidationError as e:
                raise serializers.ValidationError(str(e.message))
        return host

    def validate_changed_by(self, value):
        changed_by = User.objects.filter(username=value).first()
        if not changed_by:
            raise serializers.ValidationError('No User found from username entered.')
        return changed_by

    def get_mac(self, obj):
        return str(obj.pk)

    def get_changed_by(self, obj):
        return '%s (%s)' % (obj.changed_by.get_full_name(), obj.changed_by.username)

    class Meta:
        model = Disabled
        fields = ('host', 'mac', 'reason', 'changed_by')


class DisabledHostDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disabled
        fields = ('host',)
