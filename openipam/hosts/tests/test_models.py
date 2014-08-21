#import unittest
#import ipaddr
#from django.test import TestCase

from openipam.hosts.models import Host
#from openipam.network.models import Network, Address, Pool, HostToPool, AddressType, NetworkRange
#from openipam.dns.models import Domain, DnsRecord, DnsType
from openipam.dns.models import DnsRecord
#from openipam.user.models import User
from openipam.core.tests.test_models import IPAMTestCase

#from django.utils import timezone
from django.db import IntegrityError
#import datetime


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

    def change_and_test(self, hostname=None, mac=None, ip_address=None, instance=None):
        ip_h = Host.objects.add_or_update_host(user=self.user_model, hostname=hostname, expire_days=7, mac=mac, ip_address=ip_address, instance=instance)
        ip_h_addresses = ip_h.addresses.all()
        self.assertEqual(len(ip_h_addresses), 1)
        if ip_h_addresses:
            self.assertEqual(str(ip_h_addresses[0].address), ip_address)
        ip_h_dns = ip_h.dns_records.all()
        self.assertEqual(len(ip_h_dns), 2)
        ip_h_a = ip_h.dns_records.filter(dns_type__name='A')
        self.assertEqual(len(ip_h_a), 1)
        self.assertEqual(ip_h_a[0].name, ip_h.hostname)
        self.assertEqual(str(ip_h_a[0].ip_content), ip_address)
        ip_h_ptr = ip_h.dns_records.filter(dns_type__name='PTR')
        self.assertEqual(len(ip_h_ptr), 1)
        ip_h_ptr = ip_h_ptr[0]
        self.assertEqual(ip_h.addresses.all()[0].address.reverse_dns[:-1], ip_h_ptr.name)
        self.assertEqual(ip_h_ptr.text_content, ip_h.hostname)
        return ip_h

    def test_add_existing_hostname(self):
        with self.assertRaises(IntegrityError):
            Host.objects.create(changed_by=self.user_model, hostname='existing-host.invalid', mac='ffffff000001', expires=self.expires)

    def test_add_existing_mac(self):
        with self.assertRaises(IntegrityError):
            # MAC already exists
            Host.objects.create(changed_by=self.user_model, hostname='not-existing.invalid', mac='ffffff000000', expires=self.expires)

    def test_create_new_dynamic_host(self):
        pool_h = Host.objects.add_or_update_host(user=self.user_model, hostname='new-pool.valid', expire_days=7, mac='123456123456', pool='pool1')
        self.assertEqual(len(pool_h.addresses.all()), 0)

        pool_h_pools = pool_h.pools.all()
        self.assertEqual(len(pool_h_pools), 1)

        if pool_h_pools:
            self.assertEqual(pool_h_pools[0].name, 'pool1')

        self.assertEqual(len(pool_h.dns_records.all()), 0)

    def test_create_new_static_host(self):
        # Create host
        self.change_and_test(hostname='new-ip.valid', mac='001020304050', ip_address='192.168.1.2')

    def test_change_static_host_ip(self):
        # Create host
        h = self.change_and_test(hostname='new-ip.valid', mac='001020304050', ip_address='192.168.1.2')

        # Change IP
        h = self.change_and_test(hostname='new-ip.valid', mac='001020304050', ip_address='192.168.1.4', instance=h)
        h = self.change_and_test(ip_address='192.168.1.3', instance=h)

    def test_change_static_host_hostname(self):
        # Create host
        h = self.change_and_test(hostname='new-ip.valid', mac='001020304050', ip_address='192.168.1.2')

        # Change hostname
        h = self.change_and_test('newer-ip.valid', '001020304050', '192.168.1.2', instance=h)

    def test_change_static_host_mac(self):
        # Create host
        h = self.change_and_test('new-ip.valid', 'ab0123456789', '192.168.1.2')

        # Change MAC
        h = self.change_and_test('new-ip.valid', '001020304050', '192.168.1.2', instance=h)
        self.assertEqual(len(h.addresses.all()), 1)

    def test_change_static_ip_hostname(self):
        # Create host
        h = self.change_and_test('new-ip.valid', 'ab0123456789', '192.168.1.2')

        # Change ip, hostname
        h = self.change_and_test('still-newer-ip.valid', 'ab0123456789', '192.168.1.10', instance=h)

    def test_change_static_ip_mac(self):
        # Create host
        h = self.change_and_test('newer-ip.valid', 'ab0123000000', '192.168.1.10')

        # change ip, mac
        h = self.change_and_test('newer-ip.valid', 'ab0123ffffff', '192.168.1.99', instance=h)

    def test_change_static_hostname_mac(self):
        # Create host
        h = self.change_and_test('newer-ip.valid', 'ab0123ffffff', '192.168.1.7')

        # change hostname, mac
        h = self.change_and_test('still-newer-ip.valid', 'ab0000000000', '192.168.1.7', instance=h)

    def test_change_static_hostname_mac_ip(self):
        # Create host
        h = self.change_and_test('still-newer-ip.valid', 'ab0000000000', '192.168.1.7')

        # change hostname, mac, and IP all at once
        h = self.change_and_test('new-ip.valid', '001020304050', '192.168.1.2', instance=h)

    def test_add_addresses(self):
        host = self.change_and_test('new-ip.valid', '001020304050', '192.168.1.15')
        host.add_ip_address(self.user_model, hostname='new-ip-additional.valid', ip_address='192.168.1.20')
        self.assertEqual(len(host.addresses.all()), 2)
        self.assertEqual(str(DnsRecord.objects.get(name='new-ip-additional.valid').ip_content), '192.168.1.20')
