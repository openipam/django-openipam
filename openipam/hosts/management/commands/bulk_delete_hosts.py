from django.core.management.base import BaseCommand
import sys
import re
import os

from openipam.hosts.models import Host, User
from django.db import transaction

class Command(BaseCommand):
    MAC_ADDR_REGEX = "^([0-9A-Fa-f]{2}[:.-]?){5}[0-9A-Fa-f]{2}$"

    CYAN_ANSI_SEQ = "\033[96m"
    RED_ANSI_SEQ = "\033[91m"
    END_ANSI_SEQ = "\033[0m"

    help = (
        RED_ANSI_SEQ
        + "EXAMPLE: echo '11:11:11:11:11:11 11:11:11:11:11:12,11:11:11:11:11:13' | python3 manage.py bulk_delete_hosts --user A01234567"
        + END_ANSI_SEQ
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--file",
            help="Path to file containing line-or-comma-or-space delimited hosts",
        )
        parser.add_argument(
            "-u", "--user", help="User name to delete mac addresses with"
        )
        parser.add_argument(
            "-uid", "--user-id", help="User id to delete mac addresses with"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not bool(options["user"]) != bool(options["user_id"]):
            raise Exception("Must specify, exclusively, username or user id")

        user = (
            User.objects.filter(username=options["user"]).first()
            if options["user"]
            else User.objects.filter(pk=options["user_id"]).first()
        )

        if not user:
            raise Exception("User does not exist")

        lines = []

        if not os.isatty(sys.stdin.fileno()):
            lines += sys.stdin.readlines()

        if options["file"]:
            with open(options["file"], "r") as file:
                lines += file.readlines()

        mac_addrs = set(
            filter(
                lambda line: line,
                [
                    val
                    for sublist in [
                        line.strip().replace(",", " ").split() for line in lines
                    ]
                    for val in sublist
                ],
            )
        )

        bad_mac_addrs = list(
            filter(
                lambda mac_addr: not re.match(self.MAC_ADDR_REGEX, mac_addr), mac_addrs
            )
        )
        if bad_mac_addrs:
            raise Exception(f"Invalid mac address(es): {', '.join(bad_mac_addrs)}")
        if not mac_addrs:
            raise Exception("Did not specify any mac addresses")

        Host.objects.filter(pk__in=mac_addrs).delete(user)

        print(
            f"{self.CYAN_ANSI_SEQ}Successfully removed (if found) hosts with the following mac addresses:{self.END_ANSI_SEQ}{self.RED_ANSI_SEQ}\n  "
            + "\n  ".join(set(mac_addrs))
            + self.END_ANSI_SEQ
        )
