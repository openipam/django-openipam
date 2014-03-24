from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

from rest_framework import serializers

from openipam.hosts.models import Host, ExpirationType
from openipam.network.models import Network, Address
from openipam.api.serializers.base import MACAddressField, MultipleChoiceField, IPAddressField

from drf_compound_fields.fields import ListField, ListOrItemField

from guardian.shortcuts import get_users_with_perms, get_groups_with_perms, get_objects_for_user, assign_perm

from netaddr.core import AddrFormatError

User = get_user_model()


class HostListSerializer(serializers.ModelSerializer):
    registered_ip_address = serializers.SerializerMethodField('get_ip_address')
    is_dynamic = serializers.SerializerMethodField('get_is_dynamic')

    # def get_last_ip_seen(self, obj):
    #     return obj.last_ip_address_seen

    def get_ip_address(self, obj):
        return obj.get_ip_address

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'expires', 'description',
                  'registered_ip_address',)


class HostDetailSerializer(serializers.ModelSerializer):
    owners = serializers.SerializerMethodField('get_owners')
    registered_ip_address = serializers.SerializerMethodField('get_ip_address')
    #last_ip_address_seen = serializers.SerializerMethodField('get_last_ip_seen')
    address_type = serializers.SerializerMethodField('get_address_type')
    is_dynamic = serializers.SerializerMethodField('get_is_dynamic')

    def get_owners(self, obj):
        return obj.get_owners(ids_only=False)

    # def get_last_ip_seen(self, obj):
    #     return obj.last_ip_address_seen

    def get_ip_address(self, obj):
        return obj.get_ip_address

    def get_address_type(self, obj):
        return obj.address_type

    def get_is_dynamic(self, obj):
        return obj.is_dynamic

    class Meta:
        model = Host
        fields = ('mac', 'hostname', 'address_type', 'expires', 'is_dynamic', 'description', 'owners',
                  'registered_ip_address',)


# class HostCreateUpdateSerializer(serializers.ModelSerializer):
#     mac = MACAddressField(label='MAC Address')
#     expire_days = serializers.ChoiceField(choices=[(expire.expiration, expire.expiration) for expire in ExpirationType.objects.all()])
#     network = serializers.CharField()
#     #network = serializers.ChoiceField(choices=[(network.network, network.network) for network in Network.objects.all()])
#     ip_address = IPAddressField()
#     user_owners = ListField(serializers.CharField())
#     group_owners = ListField(serializers.CharField())

#     def validate_user_owners(self, attrs, source):
#         value_list = attrs[source]
#         for value in value_list:
#             user = User.objects.filter(username__iexact=value)
#             if not user:
#                 raise serializers.ValidationError('Please enter a valid username.')
#         return attrs

#     def validate_group_owners(self, attrs, source):
#         value_list = attrs[source]
#         for value in value_list:
#             group = Group.objects.filter(name__iexact=value)
#             if not group:
#                 raise serializers.ValidationError('Please enter a valid group.')
#         return attrs

#     def validate_mac(self, attrs, source):
#         mac = attrs[source]
#         host_exists = Host.objects.filter(mac=mac)
#         if self.object:
#             host_exists = host_exists.exclude(mac=self.instance.pk)

#         if host_exists:
#             if host_exists[0].is_expired:
#                 host_exists[0].delete()
#             else:
#                 raise serializers.ValidationError('The mac address entered already exists for host: %s.' % host_exists[0].hostname)
#         return attrs

#     def validate_hostname(self, attrs, source):
#         hostname = attrs[source]
#         host_exists = Host.objects.filter(hostname=hostname)
#         if self.object:
#             host_exists = host_exists.exclude(hostname=self.instance.hostname)

#         if host_exists:
#             if host_exists[0].is_expired:
#                 host_exists[0].delete()
#             else:
#                 raise serializers.ValidationError('The hostname entered already exists for host %s.' % host_exists[0].mac)
#         return attrs

#     def validate_network(self, attrs, source):
#         network = attrs[source]

#         try:
#             network = Network.objects.get(network=network)
#         except Network.DoesNotExist:
#             raise serializers.ValidationError('Please enter a valid network.')
#         except AddrFormatError:
#             raise serializers.ValidationError('Please enter a valid network.')

#         if network:
#             user_pools = get_objects_for_user(
#                 self.context['request'].user,
#                 ['network.add_records_to_pool', 'network.change_pool'],
#                 any_perm=True
#             )

#             address = Address.objects.filter(
#                 Q(pool__in=user_pools) | Q(pool__isnull=True),
#                 network=network,
#                 host__isnull=True,
#                 reserved=False,
#             ).order_by('address')

#             if not address:
#                 raise serializers.ValidationError('There is no addresses available from this network.'
#                                       'Please contact an IPAM Administrator.')
#         return attrs

#     def validate_ip_address(self, attrs, source):
#         ip_address = attrs[source]

#         if ip_address:
#             user_pools = get_objects_for_user(
#                 self.context['request'].user,
#                 ['network.add_records_to_pool', 'network.change_pool'],
#                 any_perm=True
#             )
#             user_nets = get_objects_for_user(
#                 self.context['request'].user,
#                 ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
#                 any_perm=True
#             )

#             address = Address.objects.filter(
#                 Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
#                 address=ip_address,
#                 host__isnull=True,
#                 reserved=False
#             )

#         if network_or_ip and network_or_ip == '1':
#             if not ip_address:
#                 raise ValidationError('This field is required.')

#             elif ip_address:
#                 # Make sure this is valid.
#                 validate_ipv46_address(ip_address)

#                 user_pools = get_objects_for_user(
#                     self.user,
#                     ['network.add_records_to_pool', 'network.change_pool'],
#                     any_perm=True
#                 )
#                 user_nets = get_objects_for_user(
#                     self.user,
#                     ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
#                     any_perm=True
#                 )

#                 address = Address.objects.filter(
#                     Q(pool__in=user_pools) | Q(pool__isnull=True) | Q(network__in=user_nets),
#                     address=ip_address,
#                     host__isnull=True,
#                     reserved=False
#                 )
#                 is_available = True if address else False

#                 if not is_available:
#                     raise ValidationError('The IP Address is reserved, in use, or not allowed.')
#                 else:
#                     self.instance.ip_address = ip_address
#         else:
#             # Clear values
#             ip_address = ''

#     class Meta:
#         model = Host
#         exclude = ('changed', 'changed_by', 'expires')
