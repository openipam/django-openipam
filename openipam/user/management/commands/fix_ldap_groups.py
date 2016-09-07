from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import fix_ldap_groups


class Command(BaseCommand):
    help = 'Fix LDAP Groups that have been asigned INTERNAL by mistake.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            dest='test',
            default=False,
            help='Use this flag to test first',
        )

    def handle(self, *args, **options):
        test = options['test']
        self.stdout.write('Fixing LDAP Groups...')
        fix_ldap_groups(test=test)
