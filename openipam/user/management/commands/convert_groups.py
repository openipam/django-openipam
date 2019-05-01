from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import convert_groups


class Command(BaseCommand):
    args = ""
    help = "Convert IPAM Groups"

    def handle(self, *args, **options):
        convert_groups()
        self.stdout.write("Converting IPAM Groups...")
