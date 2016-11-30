from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import convert_min_permissions


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    def add_arguments(self, parser):
        parser.add_option('--username',
                          dest='username',
                          default=False,
                          help='Specify a specific username to update')

    def handle(self, *args, **options):
        username = options['username'] or None
        self.stdout.write('Converting Admin Permissions...')
        convert_min_permissions(username)
