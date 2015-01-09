from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail, get_connection
from django.utils import timezone


from optparse import make_option

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import Host
from openipam.user.utils.user_utils import populate_user_from_ldap


class Command(BaseCommand):
    args = ''
    help = 'Convert Dns Type Permissions'

    option_list = BaseCommand.option_list + (
        make_option('-t', '--test',
            action='store_true',
            dest='test',
            default=False,
            help='Send as test only.  This will NOT send emails, but rather print them to the screen'),
        make_option('-c', '--count',
            action='store_true',
            dest='count',
            default=False,
            help='Display notifications counts to send but this will not send anything'),
    )

    def handle(self, *args, **options):
        test = options['test']
        count = options['count']
        connection = None
        if test:
            connection = get_connection(backend='django.core.mail.backends.console.EmailBackend')

        self.stdout.write('Sending Notifications...')

        from_address = CONFIG.get('EMAIL_ADDRESS')

        dynamic_subject = '[USU:Important] Your USU computer registrations are about to expire'
        dynamic_msg = '''%(name)s (%(username)s),

The following computer registration are going to expire soon.

If you would like to continue using the USU network for another year:

1. Log in to https://bluezone.usu.edu from on-campus (or use the VPN)
2. Click "Renew" next to the following computers:

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


        '''

        static_subject = '[USU:Important] openIPAM Host Renewal Notice'
        static_msg = '''%(name)s (%(username)s),

The following computer registrations are going to expire soon.

To renew your servers and clients for another year:

1. Log in to https://openipam.usu.edu from on-campus (or use the VPN)
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


        '''

        row_heading = "Hostname:                                MAC:                  Expiring in:   Description:"
        row_fmt = "%(hostname)-40s %(mac)-22s %(days)3s days      %(description)s"

        # Get list of people who need to be notified.
        host_qs = Host.objects.prefetch_related('pools').by_expiring(omit_guests=True)

        users_to_notify = {}
        messages = []
        bad_users = []

        for host in host_qs:
            host_users = host.get_owners(users_only=True)

            for user in host_users:
                if not user in users_to_notify:
                    users_to_notify[user] = {
                        'static': [],
                        'dynamic': []
                    }
                if host.is_static:
                    users_to_notify[user]['static'].append(host)
                else:
                    users_to_notify[user]['dynamic'].append(host)

        for user, host_types in users_to_notify.items():
            if not user.email:
                e_user = populate_user_from_ldap(user=user)
            else:
                e_user = user
            if e_user and e_user.email:
                mesg_type = 'static' if host_types.get('static') else 'dynamic'
                row_hosts = []
                for host_type, hosts in host_types.items():
                    for host in hosts:
                        row_hosts.append(row_fmt % {
                            'hostname': host.hostname,
                            'mac': host.mac,
                            'days': host.expire_days,
                            'description': host.description
                        })
                messages.append((
                    locals()['%s_subject' % mesg_type],
                    locals()['%s_msg' % mesg_type] % {
                        'name': e_user.get_full_name(),
                        'username': e_user.username,
                        'rows': '%s\n%s' % (row_heading, '\n'.join(row_hosts))
                    },
                    from_address,
                    [e_user.email]
                ))
            else:
                bad_users.append(user.username)

        if not count:
            send_mass_mail(messages, fail_silently=False, connection=connection)
            if not test:
                host_qs.update(last_notified=timezone.now())

        self.stdout.write('%s Notifications have been sent for %s hosts' % (len(messages), len(host_qs)))
        self.stdout.write('%s users have no email address.' % len(bad_users))
        self.stdout.write('\n'.join(bad_users))
