from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import populate_user_from_ldap


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    def add_arguments(self, parser):
        parser.add_argument('--username',
                            dest='username',
                            default=False,
                            help='Specify a specific username to update')

    def handle(self, *args, **options):
        username = options['username'] or None
        self.stdout.write('Populating Users...')
        populate_user_from_ldap(username=username)
