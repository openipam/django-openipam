from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    def handle(self, *args, **options):

        self.stdout.write('Adding ipam groups to users...')

        User = get_user_model()

        ipam_user_group, u_created = Group.objects.get_or_create(name='ipam-users')
        ipam_admin_group, a_created = Group.objects.get_or_create(name='ipam-admins')

        # Add Ipam Users
        for user in User.objects.all():
            user.groups.add(ipam_user_group)
            if user.is_superuser:
                user.groups.add(ipam_admin_group)

            user.save()

            self.stdout.write('User groups for %s updated' % user.username)
