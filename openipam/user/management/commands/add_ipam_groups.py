from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from openipam.user.models import User


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    def handle(self, *args, **options):

        self.stdout.write('Adding ipam groups to users...')

        ipam_user_group = Group.objects.get(name='ipam-users')
        ipam_admin_group = Group.objects.get(name='ipam-admins')

        for user in User.objects.all():
            user.groups.add(ipam_user_group)
            if user.is_superuser:
                user.groups.add(ipam_admin_group)

            user.save()


