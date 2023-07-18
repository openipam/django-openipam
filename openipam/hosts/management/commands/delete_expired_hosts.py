from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import sys

from openipam.hosts.models import Host, User
from django.db import transaction


class Command(BaseCommand):
    """Delete hosts which have been expired for a long time."""

    help = "Deletes hosts which have been expired for a long time"

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Do not delete anything, just print what would be deleted.",
        )
        parser.add_argument(
            "--static",
            action="store_true",
            dest="static",
            default=False,
            help="Delete static hosts.",
        )
        parser.add_argument(
            "--dynamic",
            action="store_true",
            dest="dynamic",
            default=False,
            help="Delete dynamic hosts.",
        )
        parser.add_argument(
            "--age",
            action="store",
            dest="age",
            type=int,
            default=None,
            help="Delete hosts that have been expired for at least this many years.",
        )
        parser.add_argument(
            "user",
            action="store",
            type=str,
            help="Log deletions as this user.",
        )

    @transaction.atomic
    def delete(self, hosts, user):
        """Delete hosts."""
        print("Deleting %d hosts" % hosts.count())
        print("Aborting at any time will restore the database to its original state")
        # Delete hosts by iterating the queryset, so that the delete() method is
        # called on each host, as this method handles the deletion of indirectly
        # related objects such as DHCP leases and DNS records.
        total = hosts.count()
        isatty = sys.stdout.isatty()
        i = -1
        try:
            for i, host in enumerate(hosts):
                # Only print progress if we are running in an interactive shell. This is
                # intended to be run primarily as a cron job, so we do not want to print a lot
                # of output in that case. Production has a logging plugin for postgresql which
                # will log the deletions, we don't need to duplicate it in the syslog. For users
                # though, having some indication that the command is actually running and how
                # complete it is is useful.
                if isatty:
                    print(
                        f"[ {i / total:6.2%} ] Deleting {str(host)} (expired {host.expires})"
                    )
                host.delete(user=user)
        except KeyboardInterrupt as e:
            # If we get a keyboard interrupt, it might be beneficial to preserve what changes
            # were made so far. If we are running in a non-interactive shell, we assume that the
            # user wants to abort the changes, as this command is primarily intended to be run
            # automatically. If we are running in an interactive shell, we ask the user if they
            # want to abort the changes, or preserve them and continue the deletion later.
            if sys.stdin.isatty():
                print(
                    "Keyboard interrupt detected. Would you like to abort the changes?"
                )
                print(
                    "Aborting will restore the database to its original state, no hosts will have been deleted."
                )
                if input("Abort changes? [Y/n] ").lower() != "n":
                    raise e

        # If we are running with interactive input, ask the user if they want to commit the
        # changes. Otherwise, commit automatically. This is to allow the user to abort the
        # changes if they are not what they expected. As this command is primarily intended to
        # be run automatically, we do not want to ask for confirmation in that case.
        if sys.stdin.isatty():
            print(f"Changes complete. {i + 1} hosts deleted.")
            if input("Commit changes? [y/N] ").lower() != "y":
                raise Exception("Aborted")
        else:
            print(f"In total, deleted {i + 1} hosts")

    def handle(self, *args, **options):
        """Handle the command."""
        dry_run = options["dry_run"]
        static = options["static"]
        dynamic = options["dynamic"]
        age = options["age"]

        # If age is not specified, default to 5 years if we are
        # deleting static hosts, 2 years otherwise.
        if not age:
            age = 5 if static else 2

        if not static and not dynamic:
            print("Must specify either --static or --dynamic")
            sys.exit(2)

        user = User.objects.filter(username=options["user"]).first()
        if not user:
            print(f"User {options['user']} does not exist")
            sys.exit(3)

        if age <= 0:
            print("Refusing to delete hosts that have not expired yet")
            sys.exit(4)

        if dry_run:
            print("Running in dry-run mode. No hosts will be deleted.")

        hosts = (
            Host.objects.select_related("mac_history")
            .filter(
                expires__lte=timezone.now() - timedelta(days=int(365.2422 * age)),
                mac_history__isnull=True,
            )
            .order_by("-expires")
        )
        # If we're only deleting one type of host, filter the queryset
        # to only include that type.
        if not static or not dynamic:
            hosts = hosts.filter(
                # Dynamic hosts have a pool, while static hosts do not.
                pools__isnull=static,
            )

        if dry_run:
            for host in hosts:
                print(f"Would delete {str(host)} (expired {host.expires})")
            print(f"In total, {hosts.count()} hosts would be deleted")
        else:
            self.delete(hosts, user)
