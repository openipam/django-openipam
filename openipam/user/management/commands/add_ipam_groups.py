from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from openipam.conf.ipam_settings import CONFIG

User = get_user_model()
UserGroup = User.groups.through


class Command(BaseCommand):
    args = ""
    help = "Convert User Permissions"

    def handle(self, *args, **options):
        self.stdout.write("Adding ipam groups to users...")

        ipam_user_group, u_created = Group.objects.get_or_create(
            name=CONFIG.get("USER_GROUP")
        )
        ipam_admin_group, a_created = Group.objects.get_or_create(
            name=CONFIG.get("ADMIN_GROUP")
        )

        # Add Ipam Users
        all_users = (
            User.objects.exclude(groups=ipam_user_group).exclude(pk=-1).distinct()
        )
        super_users = (
            User.objects.exclude(groups=ipam_admin_group)
            .exclude(pk=-1)
            .filter(is_superuser=True)
            .distinct()
        )
        add_user_list = []

        for user in all_users:
            add_user_list.append(UserGroup(user=user, group=ipam_user_group))

        for user in super_users:
            add_user_list.append(UserGroup(user=user, group=ipam_admin_group))

        UserGroup.objects.bulk_create(add_user_list)

        self.stdout.write("IPAM Groups added.")
