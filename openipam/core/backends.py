from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from cacheops import invalidate_model


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

    def _mirror_groups(self):
        """
        Mirrors the user's LDAP groups in the Django database and updates the
        user's membership.
        """
        # groups = set([Group.objects.get_or_create(name=group_name)[0] for group_name
        #     in group_names] + [group for group in self._user.groups.all()])

        group_names = self._get_groups().get_group_names()
        user_groups = self._user.groups.all()

        db_groups_names = set([group.name for group in Group.objects.all()])
        groups_to_add = list(group_names - db_groups_names)

        new_groups = []
        if groups_to_add:
            invalidate_model(Group)
            Group.objects.bulk_create([Group(name=group) for group in groups_to_add])
            new_groups = Group.objects.filter(name__in=groups_to_add)

        groups = set(new_groups + [group for group in user_groups])

        self._user.groups = groups



