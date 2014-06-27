from django.core.management.base import BaseCommand, CommandError
# FIXME: optparse is deprecated, has django switched to argparse?
from optparse import make_option

from openipam.core.utils.networks_stats_carbon import push_data


class Command(BaseCommand):
    #args = '[-l|--update-locations] [-r|--send-report] [-E|--no-update-endpoints]'
    help = 'Push network lease usage data to carbon server'
    option_list = BaseCommand.option_list + (
        make_option('-s', '--server', action='store',
                    dest='server', default=False,
                    help='server host'),
        make_option('-p', '--port', action='store',
                    dest='port', default=False,
                    help='server port'),
    )

    def handle(self, *args, **options):
        server = options['server']
        if not server:
            raise CommandError("Must specify a server")
        port = options['port']
        if not port:
            port = 2003
        else:
            port = int(port)

        push_data(server, port)
