from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

from openipam.log.models import EmailLog
from openipam.user.models import AuthSource

# Dont require this.
try:
    from django_auth_ldap.backend import LDAPBackend, _LDAPUser
    from django_cas_ng.backends import CASBackend
except ImportError:
    pass

import re

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
            self.logger.debug("Rejecting empty password for %s" % username)
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
    # TODO: We need to hash out LDAP and Internal Groups with the same name.
    # def _mirror_groups(self):
    #     """
    #     Mirrors the user's LDAP groups in the Django database and updates the
    #     user's membership.
    #     """
    #     # groups = set([Group.objects.get_or_create(name=group_name)[0] for group_name
    #     #     in group_names] + [group for group in self._user.groups.all()])

    #     source = AuthSource.objects.get(name='LDAP')

    #     # Get Central groups and create if necessary
    #     group_names = self._get_groups().get_group_names()
    #     user_groups = populate_central_groups(group_names, source)

    #     # Get Static User Groups
    #     static_user_groups = self._user.groups.exclude(source__source=source)

    #     # Set the Groups to the User
    #     groups = static_user_groups | user_groups

    #     self._user.groups = groups

    def _mirror_groups(self):
        source = AuthSource.objects.get(name="LDAP")
        source_id = source.pk

        target_group_names = frozenset(self._get_groups().get_group_names())
        # current_group_names = frozenset(self._user.groups.values_list('name', flat=True).iterator())
        static_groups = list(
            self._user.groups.exclude(source__source=source).iterator()
        )

        # if target_group_names != current_group_names:
        existing_groups = list(
            Group.objects.filter(name__in=target_group_names).iterator()
        )

        new_groups = []
        for name in target_group_names:
            if name not in existing_groups:
                obj, created = Group.objects.get_or_create(name=name)
                if obj.source.source_id != source_id:
                    obj.source.source_id = source_id
                    obj.source.save()
                new_groups.append(obj)

        self._user.groups = static_groups + existing_groups + new_groups


class LoggingEmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        message_len = super(LoggingEmailBackend, self).send_messages(email_messages)
        try:
            for email_message in email_messages:
                EmailLog.objects.create(
                    to="; ".join(email_message.recipients()),
                    subject=email_message.subject,
                    body=email_message.body,
                )
        except Exception:
            pass
        return message_len


class ConsoleLoggingEmailBackend(ConsoleEmailBackend):
    def send_messages(self, email_messages):
        message_len = super(ConsoleLoggingEmailBackend, self).send_messages(
            email_messages
        )
        try:
            for email_message in email_messages:
                EmailLog.objects.create(
                    to="; ".join(email_message.recipients()),
                    subject=email_message.subject,
                    body=email_message.body,
                )
        except Exception:
            pass
        return message_len


class IPAMCASBackend(CASBackend):
    def authenticate(self, ticket, service, request):
        self.user = super(IPAMCASBackend, self).authenticate(ticket, service, request)

        if self.user:
            self.request = request
            self._mirror_groups()

            # Get LDAP source
            # source = AuthSource.objects.get(name='LDAP')

            # group_names = self._get_group_names(request)
            # if group_names:
            #     user_groups = populate_central_groups(group_names, source)
            #     for group in user_groups:
            #         user.groups.add(group)

        return self.user

    def _get_group_names(self):
        group_names = []
        attributes = self.request.session.get("attributes", {})
        if attributes.get("memberOf", None):
            group_names_str = "".join(attributes["memberOf"])
            pattern = re.compile("CN=([^,]*)")
            group_names = pattern.findall(group_names_str)
        return group_names

    def _mirror_groups(self):
        source = AuthSource.objects.get(name="LDAP")
        source_id = source.pk

        target_group_names = frozenset(self._get_group_names())
        # current_group_names = frozenset(self._user.groups.values_list('name', flat=True).iterator())
        static_groups = list(self.user.groups.exclude(source__source=source).iterator())

        # if target_group_names != current_group_names:
        existing_groups = list(
            Group.objects.filter(name__in=target_group_names).iterator()
        )

        new_groups = []
        for name in target_group_names:
            if name not in existing_groups:
                obj, created = Group.objects.get_or_create(name=name)
                if obj.source.source_id != source_id:
                    obj.source.source_id = source_id
                    obj.source.save()
                new_groups.append(obj)

        self.user.groups = static_groups + existing_groups + new_groups
