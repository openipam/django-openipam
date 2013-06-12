from django.core.management.base import BaseCommand, CommandError



class Command(BaseCommand):
    args = ''
    help = 'Convert User Permissions'

    def handle(self, *args, **options):
        pass
