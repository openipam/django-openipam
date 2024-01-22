# Host expiration notification

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, send_mass_mail, get_connection

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import Host
from openipam.user.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from openipam.user.utils.user_utils import populate_user_from_ldap

from guardian.models import UserObjectPermission, GroupObjectPermission

from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    args = ""
    help = "Script for Auto Renewals and Notifications for hosts due to expire."

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--test",
            action="store_true",
            dest="test",
            default=False,
            help="Send as test only.  This will NOT send emails or auto renew, but rather print them to the screen",
        )
        parser.add_argument(
            "-c",
            "--count",
            action="store_true",
            dest="count",
            default=False,
            help="Display notifications counts to send but this will not send anything",
        )
        parser.add_argument(
            "-n",
            "--noasync",
            action="store_true",
            dest="noasync",
            default=False,
            help="This flag will sent using send_mail instead of send_mass_mail",
        )

    def handle(self, *args, **options):
        test = options["test"]
        count = options["count"]
        noasync = options["noasync"]
        connection = None
        if test:
            connection = get_connection(
                backend="django.core.mail.backends.console.EmailBackend"
            )

        self.stdout.write("Sending Notifications...")

        from_address = CONFIG.get("NOTIFICATION_EMAIL_ADDRESS")

        dynamic_subject = (
            "[USU:Important] Your USU device registrations are about to expire"
        )
        dynamic_msg = """%(name)s (%(username)s),

The following device registrations are going to expire soon.

If you would like to continue using the USU network for another year:

1. If you are on the USU network, you can log in at https://netreg.usu.edu/ .
   However, if you are not on the USU network you must first connect your device to the
   network using VPN and then go to https://netreg.usu.edu/ and login.
2. Click "Renew" next to the following devices:

%(rows)s

Instructions on using the VPN server may be found at http://it.usu.edu/vpn.

If you have any questions, please contact the IT Service Desk.

Remember: never give your password to anyone, including USU employees.

--
IT Service Desk

Fall & Spring Hours
Mon-Thurs: 8:00am-8:00pm
Friday: 8:00am-6:00pm
Saturday: 10:00am-3:00pm

Summer Hours
Mon-Fri: 8:00am-6:00pm
Saturday: Closed

Contact us at:
Phone: 797-HELP (4357)
Toll Free: 877-878-8325
Email: servicedesk@usu.edu
http://usu.service-now.com (Issue Tracking System)


        """

        static_subject = "[USU:Important] openIPAM Host Renewal Notice"
        static_msg = """%(name)s (%(username)s),

The following device registrations are going to expire soon.

To renew your servers and clients for another year:

1. If you are on the USU network, you can log in at https://openipam.usu.edu/ . However, if you are
   not on the USU network you must first connect your device to the network using VPN
   and then go to https://openipam.usu.edu/ and login.
2. Click on the "Hosts" tab in the upper left to view hosts.
3. Click "Show Mine" to view your hosts.  You can sort your hosts by expiration date if you wish.
4. Check the boxes next to those hosts you wish to renew.
5. Select the "Choose an action" drop down and then select "Renew selected hosts" followed by the "Go" button.

Instructions on using the VPN server may be found at http://it.usu.edu/vpn.

Remember: help us keep up-to-date data. Don't renew hosts you don't need.

%(rows)s

If you have any questions, please contact the IT Service Desk.

--
IT Service Desk

Fall & Spring Hours
Mon-Thurs: 8:00am-8:00pm
Friday: 8:00am-6:00pm
Saturday: 10:00am-3:00pm

Summer Hours
Mon-Fri: 8:00am-6:00pm
Saturday: Closed

Contact us at:
Phone: 797-HELP (4357)
Toll Free: 877-878-8325
Email: servicedesk@usu.edu
http://usu.service-now.com (Issue Tracking System)


        """

        row_heading = "Hostname:                                MAC:                  Expiring in:   Description:"
        row_fmt = "%(hostname)-40s %(mac)-22s %(days)3s days      %(description)s"

        # Get list of people who need to be notified.
        host_qs = (
            Host.objects.prefetch_related("pools")
            .by_expiring(omit_guests=True)
            .select_related("mac_history")
        )
        # Check to see if the user has the is_owner_host permission
        # Sync the user's email and groups from LDAP if they do.
        perm = Permission.objects.get(codename="is_owner_host")
        ctype = ContentType.objects.get(model="host")
        users_sync = UserObjectPermission.objects.filter(
            permission=perm, content_type=ctype, object_pk__in=[h.mac for h in host_qs]
        )
        group_sync = GroupObjectPermission.objects.filter(
            permission=perm, content_type=ctype, object_pk__in=[h.mac for h in host_qs]
        )
        users_sync = [u.user for u in users_sync]
        group_sync = [g.group.user_set.all() for g in group_sync]
        group_sync = [u for g in group_sync for u in g]
        to_sync = set(users_sync + group_sync)
        for user in to_sync:
            self.stdout.write(f"Updating {user.username} email and groups from LDAP...")
            populate_user_from_ldap(user=user)

        users_to_notify = {}
        messages = []
        bad_users = []
        admin_user = User.objects.get(username="admin")
        for host in host_qs:
            host_users = host.get_owners(users_only=True)
            try:
                mac_last_seen = host.mac_history.stopstamp
                current_time = timezone.now()
                thirty_days_ago = current_time - timedelta(days=30)
                if thirty_days_ago <= mac_last_seen <= current_time:
                    self.stdout.write(
                        f"Host {host.hostname} will auto renew for 30 days"
                    )
                    if not test:
                        host.expire_days = 30
                        host.user = admin_user
                        host.set_expiration(host.expire_days)
                        host.save(force_update=True)

                    continue
            except Host.mac_history.RelatedObjectDoesNotExist:
                pass

            for user in host_users:
                if user not in users_to_notify:
                    users_to_notify[user] = {"static": [], "dynamic": []}
                if host.is_static:
                    users_to_notify[user]["static"].append(host)
                else:
                    users_to_notify[user]["dynamic"].append(host)

        for user, host_types in list(users_to_notify.items()):
            # if not user.email:
            #     e_user = populate_user_from_ldap(user=user)
            # else:
            e_user = user
            if e_user and e_user.email:
                mesg_type = "static" if host_types.get("static") else "dynamic"
                row_hosts = []
                for host_type, hosts in list(host_types.items()):
                    for host in hosts:
                        row_hosts.append(
                            row_fmt
                            % {
                                "hostname": host.hostname,
                                "mac": host.mac,
                                "days": host.expire_days,
                                "description": host.description,
                            }
                        )
                messages.append(
                    (
                        locals()["%s_subject" % mesg_type],
                        locals()["%s_msg" % mesg_type]
                        % {
                            "name": e_user.get_full_name(),
                            "username": e_user.username,
                            "rows": "%s\n%s" % (row_heading, "\n".join(row_hosts)),
                        },
                        from_address,
                        [e_user.email],
                    )
                )
            else:
                bad_users.append(user.username)

        if not count:
            if noasync:
                for message in messages:
                    self.stdout.write("Sending email to %s..." % ",".join(message[3]))
                    send_mail(*message, fail_silently=False, connection=connection)
            else:
                send_mass_mail(messages, fail_silently=False, connection=connection)

            if not test:
                host_qs.update(last_notified=timezone.now())

        self.stdout.write(
            "%s Notifications have been sent for %s hosts"
            % (len(messages), len(host_qs))
        )
        self.stdout.write("%s users have no email address." % len(bad_users))
        self.stdout.write("\n".join(bad_users))
