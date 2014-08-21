#import unittest
#import ipaddr
from django.test import TestCase

from openipam.hosts.models import Host
from openipam.network.models import Network, Address, Pool, HostToPool, AddressType, NetworkRange
from openipam.dns.models import Domain, DnsRecord, DnsType
from openipam.user.models import User

from django.utils import timezone
#from django.db import IntegrityError
import datetime


class IPAMTestCase(TestCase):
    user = {'username': 'admin', 'first_name': 'Some', 'last_name': 'Admin',
            'is_superuser': True, 'is_staff': False, 'is_active': True, }
    expires = timezone.now() + datetime.timedelta(days=7)
    networks = None
    dns_domains = None
    dns_records = None
    hosts = None
    fixtures = ['initial_data']

    def _add_network(self, network, user):
            obj = Network.objects.create(changed_by=user, **network)
            addresses = []
            for address in obj.network:
                reserved = False
                if address in (obj.gateway, obj.network[0], obj.network[-1]):
                    reserved = True
                addresses.append(
                    #TODO: Need to set pool eventually.
                    Address(address=address, network=obj, reserved=reserved, changed_by=user)
                )
            return Address.objects.bulk_create(addresses)

    def _add_dns_record(self, record, user):
            if type(record['dns_type']) in (str, unicode):
                record['dns_type'] = DnsType.objects.get(name=record['dns_type'])
            if 'ip_content' in record and type(record['ip_content']) == str:
                    record['ip_content'] = Address.objects.get(address=record['ip_content'])
            if 'did' not in record:
                parts = record['name'].split('.')
                possible_domains = []
                for i in xrange(len(parts)):
                    possible_domains.append('.'.join(parts[i:]))
                domain = Domain.objects.filter(name__in=possible_domains).extra(select={'name_length': 'length(name)'}).order_by('name_length')[0]
                record['domain'] = domain
            return DnsRecord.objects.create(changed_by=user, **record)

    def _add_host_record(self, host, user):
            address = None
            pool = None
            if 'address' in host:
                address = host['address']
                del host['address']
            if 'pool' in host:
                pool = host['pool']
                del host['pool']
            if 'expires' not in host:
                host['expires'] = self.expires

            host = Host.objects.create(changed_by=user, **host)
            if address:
                a_obj = Address.objects.get(address=address)
                a_obj.mac = host.mac
                a_obj.pool = None
                a_obj.save()
            if pool:
                p_obj = Pool.objects.get(name=pool)
                HostToPool.objects.create(host=host, pool=p_obj, changed_by=user)
            return host

    def _add_address_type(self, atype, user):
            ranges = None
            if 'ranges' in atype:
                ranges = atype['ranges']
                del atype['ranges']
            if 'pool' in atype:
                atype['pool'] = Pool.objects.get(name=atype['pool'])
            at = AddressType.objects.create(**atype)

            if ranges:
                for r in ranges:
                    r_obj = NetworkRange.objects.get_or_create(range=r)[0]
                    at.ranges.add(r_obj)

            return at

    def setUp(self):
        user = User.objects.create(**self.user)
        self.user_model = user

        for address_type in self.address_types:
            self._add_address_type(address_type, user)

        for pool in self.pools:
            Pool.objects.create(**pool)

        for network in self.networks:
            self._add_network(network, user)

        for domain in self.dns_domains:
            Domain.objects.create(changed_by=user, **domain)

        for rec in self.dns_records:
            self._add_dns_record(rec.copy(), user)

        for host in self.hosts:
            self._add_host_record(host.copy(), user)
