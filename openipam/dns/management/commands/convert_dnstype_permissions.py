from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from openipam.conf.ipam_settings import CONFIG
from openipam.dns.models import DnsType

from guardian.shortcuts import assign_perm


class Command(BaseCommand):
    args = ""
    help = "Convert Dns Type Permissions"

    def handle(self, *args, **options):

        self.stdout.write("Converting DNS Type Permissions")

        dns_types = DnsType.objects.exclude(min_permissions__name="NONE")
        ipam_user_group = Group.objects.get(name=CONFIG.get("USER_GROUP"))

        for dns_type in dns_types:
            assign_perm("add_records_to_dnstype", ipam_user_group, dns_type)

            self.stdout.write("Permission for %s updated" % dns_type.name)
