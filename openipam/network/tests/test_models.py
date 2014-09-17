#import unittest
#import ipaddr
#from django.test import TestCase

from openipam.hosts.models import Host
#from openipam.network.models import Network, Address, Pool, HostToPool, AddressType, NetworkRange
#from openipam.dns.models import Domain, DnsRecord, DnsType
#from openipam.dns.models import DnsRecord
#from openipam.user.models import User
from openipam.core.tests.test_models import IPAMTestCase

#from django.utils import timezone
#from django.db import IntegrityError
#import datetime


class AddressTest(IPAMTestCase):

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

        return super(AddressTest, self).setUp()

    def change_and_test_address(self, hostname=None, mac=None, ip_address=None, instance=None):
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

    def test_create_network(self):
        # create network
        # check stuff
        self.assertEqual(1, 0)

    def test_release_address(self):
        # release address
        # check DNS records
        # check address.pool
        self.assertEqual(1, 0)

    def test_assign_address(self):
        # assign address
        # check stuff
        self.assertEqual(1, 0)
