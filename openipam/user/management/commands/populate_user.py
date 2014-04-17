from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import populate_user_from_ldap
from optparse import make_option


class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    option_list = BaseCommand.option_list + (
        make_option('--username',
            dest='username',
            default=False,
            help='Specify a specific username to update'),
    )

    def handle(self, *args, **options):
        username = options['username'] or None
        self.stdout.write('Populating Users...')
        populate_user_from_ldap(username=username)
