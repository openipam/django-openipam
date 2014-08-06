"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from openipam.hosts.models import Host

HOST_LIST = [
    {
        'user': 'admin',
        'mac': 'D2-C9-BA-83-8C-96',
        'hostname': 'test.usu.edu',
        'expire_days': '30'
    }
]


class HostTestCase(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


    def add_host(self):
        for host in HOST_LIST:
            Host.objects.add_or_update_host(**host)
