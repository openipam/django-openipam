from django.core.management.base import BaseCommand
from openipam.user.utils.user_utils import sync_active_users


class Command(BaseCommand):
    args = ""
    help = "Sync LDAP Users who have permissions"

    def handle(self, *args, **options):
        self.stdout.write("Syncing Users...")
        sync_active_users()
        self.stdout.write("Syncing complete.")
