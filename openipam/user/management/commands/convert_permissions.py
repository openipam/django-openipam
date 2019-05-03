from django.core.management.base import BaseCommand, CommandError
from openipam.user.utils.user_utils import convert_host_permissions, convert_permissions


class Command(BaseCommand):
    args = ""
    help = "Convert User Permissions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            dest="delete",
            default=False,
            help="Delete poll instead of closing it",
        )

        parser.add_argument(
            "--username",
            dest="username",
            default=False,
            help="Specify a specific username to update",
        )

        parser.add_argument(
            "--groupname",
            dest="groupname",
            default=False,
            help="Specify a specific groupname to update",
        )

    def handle(self, *args, **options):
        delete = options["delete"]
        username = options["username"] or None
        groupname = options["groupname"] or None
        if not groupname:
            self.stdout.write("Converting Host Permissions...")
            convert_host_permissions(delete=delete, username=username)
        self.stdout.write("Converting Group Permissions...")
        convert_permissions(delete=delete, username=username, groupname=groupname)
