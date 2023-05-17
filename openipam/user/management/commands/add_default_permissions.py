from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db.models.loading import get_model

from guardian.shortcuts import assign_perm

from openipam.conf.ipam_settings import CONFIG


class Command(BaseCommand):
    args = ""
    help = "Add Default Permissions"

    def handle(self, *args, **options):

        self.stdout.write("Adding default permissions to ipam-users group...")

        ipam_user_group, u_created = Group.objects.get_or_create(
            name=CONFIG.get("USER_GROUP")
        )
        ipam_admin_group, a_created = Group.objects.get_or_create(
            name=CONFIG.get("ADMIN_GROUP")
        )

        default_perms = CONFIG.get("DEFAULT_PERMISSIONS")

        for app, model in list(default_perms.items()):
            for model, lst in list(model.items()):
                for pk in lst:
                    instance = get_model(app, model).objects.get(pk=pk)
                    assign_perm("add_records_to_%s" % model, ipam_user_group, instance)

        self.stdout.write("Default Permissions added.")
