from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from guardian.shortcuts import assign_perm

from openipam.network.models import Network


class Command(BaseCommand):
    args = ""
    help = "Add Group Permissions in Bulk"

    def add_arguments(self, parser):
        parser.add_argument("--group", nargs="?", required=True)
        parser.add_argument("--perm", nargs="?", required=True)
        parser.add_argument("--objects", nargs="+", required=False)
        parser.add_argument("--cidr", nargs="?")

    def handle(self, *args, **options):
        self.stdout.write("Adding default permissions to ipam-users group...")
        perm = options["perm"]
        group = Group.objects.get(name__iexact=options["group"])
        if options.get("cidr"):
            objects = Network.objects.filter(
                network__net_contained_or_equal=options["cidr"]
            )
        else:
            objects = (
                ContentType.objects.get(permission__codename=options["perm"])
                .model_class()
                .objects.filter(pk__in=options["objects"])
            )

        for obj in objects:
            assign_perm(perm, group, objects)
            self.stdout.write(f"{obj} Permissions added to {group}.")

        self.stdout.write("Bulk Permissions added.")
