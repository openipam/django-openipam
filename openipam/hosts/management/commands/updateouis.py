from django.core.management.base import BaseCommand
from openipam.hosts.management.oui_import import import_ouis

from optparse import make_option


class Command(BaseCommand):
    args = ''
    help = 'Update OUI table used to display manufacturer info'

    option_list = BaseCommand.option_list + (
        make_option('-u', '--url',
                    help="URL for wireshark 'manuf'-style file"),
    )

    def handle(self, *args, **options):

        url = options.get('url', None)

        if url:
            import_ouis(manuf=url)
        else:
            import_ouis()

