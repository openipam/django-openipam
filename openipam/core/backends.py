from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

from openipam.log.models import EmailLog
from openipam.user.models import GroupSource, AuthSource

# Dont require this.
try:
    from django_auth_ldap.backend import LDAPBackend, _LDAPUser
except:
    pass

User = get_user_model()


class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Modified django auth ldap backend to allow mirroring of groups and still
# keep static groups that are django only.
class IPAMLDAPBackend(LDAPBackend):

    def authenticate(self, username, password):
        if len(password) == 0 and not self.settings.PERMIT_EMPTY_PASSWORD:
            logger.debug('Rejecting empty password for %s' % username)
            return None

        ldap_user = _IPAMLDAPUser(self, username=username.strip())
        user = ldap_user.authenticate(password)

        return user

    def populate_user(self, username):
        ldap_user = _IPAMLDAPUser(self, username=username)
        user = ldap_user.populate_user()

        return user


class _IPAMLDAPUser(_LDAPUser):

    # TODO: How can we take users out of LDAP groups?
    def _mirror_groups(self):
        """
        Mirrors the user's LDAP groups in the Django database and updates the
        user's membership.
        """
        # groups = set([Group.objects.get_or_create(name=group_name)[0] for group_name
        #     in group_names] + [group for group in self._user.groups.all()])

        # Get LDAP source
        source = AuthSource.objects.get(name='LDAP')
        # Get the LDAP group names from LDAP for user
        user_ldap_group_names = self._get_groups().get_group_names()
        # Get existing LDAP groups.
        existing_ldap_groups_names = set([group.name for group in Group.objects.filter(name__in=user_ldap_group_names)])
        # Get groups to add
        groups_to_add = list(user_ldap_group_names - existing_ldap_groups_names)

        # Add new LDAP groups
        if groups_to_add:
            for group in groups_to_add:
                Group.objects.get_or_create(name=group)

        # Group.objects.bulk_create([Group(name=group) for group in groups_to_add])
        ldap_user_groups = Group.objects.select_related('source').filter(name__in=[group for group in user_ldap_group_names])

        # Make sure all LDAP groups are sources as LDAP
        for group in ldap_user_groups:
            try:
                assert group.source
            except:
                group.save()
        GroupSource.objects.filter(group__in=ldap_user_groups).update(source=source)

        # Get Static User Groups
        static_user_groups = self._user.groups.exclude(source__source=source)

        # Set the Groups to the User
        groups = static_user_groups | ldap_user_groups
        self._user.groups = groups


class LoggingEmailBackend(EmailBackend):

    def send_messages(self, email_messages):
        message_len = super(LoggingEmailBackend, self).send_messages(email_messages)
        try:
            for email_message in email_messages:
                EmailLog.objects.create(
                    to='; '.join(email_message.recipients()),
                    subject=email_message.subject, body=email_message.body,
                    )
        except:
            pass
        return message_len


class ConsoleLoggingEmailBackend(ConsoleEmailBackend):

    def send_messages(self, email_messages):
        message_len = super(LoggingEmailBackend, self).send_messages(email_messages)
        try:
            for email_message in email_messages:
                EmailLog.objects.create(
                    to='; '.join(email_message.recipients()),
                    subject=email_message.subject, body=email_message.body,
                    )
        except:
            pass
        return message_len
