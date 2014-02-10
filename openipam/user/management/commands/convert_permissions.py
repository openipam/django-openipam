from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import convert_host_permissions, convert_permissions
from optparse import make_option


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete poll instead of closing it'),

        make_option('--username',
            dest='username',
            default=False,
            help='Specify a specific username to update'),
    )

    def handle(self, *args, **options):
        delete = options['delete']
        username = options['username'] or None
        self.stdout.write('Converting Host Permissions...')
        convert_host_permissions(delete=delete, username=username)
        self.stdout.write('Converting Group Permissions...')
        convert_permissions(delete=delete, username=username)
