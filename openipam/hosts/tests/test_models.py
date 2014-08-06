#import unittest
#import ipaddr
from django.test import TestCase

from openipam.hosts.models import Host
from openipam.network.models import Network, Address, Pool, HostToPool, AddressType, NetworkRange
from openipam.dns.models import Domain, DnsRecord, DnsType
from openipam.user.models import User

from django.utils import timezone
from django.db import IntegrityError
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


class HostTest(IPAMTestCase):

    def setUp(self):
        self.networks = [
            {
                'network': '192.168.{}.0/24'.format(i),
                'name': 'rfc1918-192-168-{}'.format(i),
                'gateway': '192.168.{}.1'.format(i),
            } for i in range(4)]

        self.dns_domains = [{'name': i, 'type': 'NATIVE'} for i in ['valid', 'invalid', '168.192.in-addr.arpa']]

        self.dns_records = [
            {'name': 'existing-a.invalid', 'dns_type': 'A', 'ip_content': '192.168.1.2'},
            {'name': 'existing-cname.invalid', 'dns_type': 'CNAME', 'text_content': 'existing-a.invalid'},
            {'name': 'existing-txt.invalid', 'dns_type': 'TXT', 'text_content': 'ignored value'},
            {'name': '_someproto._tcp.existing-srv.invalid', 'dns_type': 'SRV', 'priority': 0, 'text_content': '5 12345 existing-a.invalid'},
        ]

        self.hosts = [
            {'hostname': 'existing-host.invalid', 'mac': 'ffffff000000', 'address': '192.168.0.3'}
        ]

        self.pools = [
            {'name': 'pool1', 'description': '', 'allow_unknown': False, 'lease_time': 1800, 'assignable': False, }
        ]

        self.address_types = [
            {'name': 'address_type_1', 'description': '', 'pool_id': None, 'is_default': False, 'ranges': ['192.168.3.0/24', ], }
        ]

        return super(HostTest, self).setUp()

    def test_add_existing_hostname(self):
        with self.assertRaises(IntegrityError):
            Host.objects.create(changed_by=self.user_model, hostname='existing-host.invalid', mac='ffffff000001', expires=self.expires)

    def test_add_existing_mac(self):
        with self.assertRaises(IntegrityError):
            # MAC already exists
            Host.objects.create(changed_by=self.user_model, hostname='not-existing.invalid', mac='ffffff000000', expires=self.expires)

    def test_create_new_hosts(self):
        pool_h = Host.objects.add_or_update_host(user=self.user_model, hostname='new-pool.valid', expire_days=7, mac='123456123456', pool='pool1')
        self.assertEqual(len(pool_h.addresses.all()), 0)

        pool_h_pools = pool_h.pools.all()
        self.assertEqual(len(pool_h_pools), 1)

        if pool_h_pools:
            self.assertEqual(pool_h_pools[0].name, 'pool1')
      
        self.assertEqual(len(pool_h.dns_records.all()), 0)

        ip_h = Host.objects.add_or_update_host(user=self.user_model, hostname='new-ip.valid', expire_days=7, mac='123456123456', ip_address='192.168.1.2')
        ip_h_addresses = ip_h.addresses.all()
        self.assertEqual(len(ip_h_addresses), 1)
        if ip_h_addresses:
            self.assertEqual(str(ip_h_addresses[0].address), '192.168.1.2')

        ip_h_dns = ip_h.dns_records.all()
        self.assertEqual(len(ip_h_dns), 2)
        ip_h_a = ip_h.dns_records.filter(dns_type__name='A')
        self.assertEqual(len(ip_h_a), 1)
        self.assertEqual(ip_h_a[0].name, ip_h.hostname)
        self.assertEqual(str(ip_h_a[0].ip_content), '192.168.1.2')
        ip_h_ptr = ip_h.dns_records.filter(dns_type__name='PTR')
        self.assertEqual(len(ip_h_ptr), 1)
        print dir(ip_h_addresses[0].address)
        self.assertEqual(ip_h.addresses.all()[0].address.reverse_dns()[:-1], ip_h_ptr.name)
        self.assertEqual(ip_h_ptr.text_content, ip_h.hostname)
        
        net_h = Host.objects.add_or_update_host(user=self.user_model, hostname='new-net.valid', expire_days=7, mac='123456123456', network=Network.objects.get(network='192.168.1.0/24'))
