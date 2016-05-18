from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import populate_user_from_ldap, sync_active_users
from optparse import make_option


class Command(BaseCommand):
    args = ''
    help = 'Sync LDAP Users who have permissions'

    def handle(self, *args, **options):
        self.stdout.write('Syncing Users...')
        sync_active_users()
        self.stdout.write('Syncing complete.')
