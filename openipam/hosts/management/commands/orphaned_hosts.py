from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from openipam.hosts.management.oui_import import import_ouis
from openipam.hosts.models import Host

from optparse import make_option

from guardian.models import UserObjectPermission, GroupObjectPermission


class Command(BaseCommand):
    args = ''
    help = 'Find expired hosts with no owner.'

    option_list = BaseCommand.option_list + (
        make_option('-d', '--delete',
                    help="Delete Hosts"),
    )

    def handle(self, *args, **options):

        delete = options.get('delete', None)

        ct = ContentType.objects.get(app_label='hosts', model='host')
        user_hosts_with_perms = [uop.object_pk for uop in UserObjectPermission.objects.filter(content_type=ct)]
        group_hosts_with_perms = [gop.object_pk for gop in GroupObjectPermission.objects.filter(content_type=ct)]

        hosts_with_perms = Host.objects.raw('''
            SELECT hosts.mac from hosts where host.mac in %s or hosts.mac in %s
        ''', [user_hosts_with_perms, group_hosts_with_perms])

        orphaned_hosts = Host.objects.filter(expires__lt=timezone.now()).exclude(mac__in=[host.pk for host in hosts_with_perms])

        self.stdout.write('%s hosts are epired and have no owner.' % len(orphaned_hosts))
        self.stdout.write('\n'.join(orphaned_hosts))

