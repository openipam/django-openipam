from django.db import models
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup
from django.utils import timezone
from django.utils.http import urlquote
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils.functional import cached_property

from openipam.user.managers import UserToGroupManager, IPAMUserManager
from openipam.user.signals import assign_ipam_groups, force_usernames_uppercase, \
   remove_obj_perms_connected_with_user, add_group_souce


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    email = models.EmailField(_('email address'), max_length=255, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # TODO: Remove later
    min_permissions = models.ForeignKey('Permission', db_column='min_permissions', blank=True, null=True,
                                        related_name='user_min_permissions')
    source = models.ForeignKey('AuthSource', db_column='source', blank=True, null=True)

    objects = IPAMUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.username

    @cached_property
    def is_ipamadmin(self):
        if self.is_superuser:
            return True
        else:
            groups = [group.name for group in self.groups.all()]
            return True if 'ipam-admins' in groups else False

    @cached_property
    def network_owner_perms(self):
        if self.has_perm('network.is_owner_network'):
            return True
        else:
            from openipam.network.models import Network
            return Network.objects.by_owner(self, use_groups=True, ids_only=True)

    @cached_property
    def domain_owner_perms(self):
        if self.has_perm('dns.is_owner_domain'):
            return True
        else:
            from openipam.dns.models import Domain
            return Domain.objects.by_owner(self, use_groups=True, names_only=True)

    @cached_property
    def host_owner_perms(self):
        if self.has_perm('hosts.is_owner_host'):
            return True
        else:
            from openipam.hosts.models import Host
            return Host.objects.by_owner(self, use_groups=True, ids_only=True)

    # @cached_property
    # def network_change_perms(self):
    #     if self.has_perm('network.change_network') or self.has_perm('network.is_owner_network'):
    #         return True
    #     else:
    #         from openipam.network.models import Network
    #         return Network.objects.by_change_perms(self, ids_only=True)

    # @cached_property
    # def domain_change_perms(self):
    #     if self.has_perm('dns.change_domain') or self.has_perm('dns.is_owner_domain'):
    #         return True
    #     else:
    #         from openipam.dns.models import Domain
    #         return Domain.objects.by_change_perms(self, names_only=True)

    # @cached_property
    # def host_change_perms(self):
    #     if self.has_perm('hosts.change_host') or self.has_perm('dns.is_owner_host'):
    #         return True
    #     else:
    #         from openipam.hosts.models import Host
    #         return Host.objects.by_change_perms(self, ids_only=True)

    def get_auth_user(self):
        try:
            return AuthUser.objects.get(username=self.username)
        except AuthUser.DoesNotExist:
            return None

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    # def get_ipam_groups(self):
    #     return Group.objects.filter(group_users__user=self)

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')


class GroupSource(models.Model):
    group = models.OneToOneField(AuthGroup, primary_key=True, related_name='source')
    source = models.ForeignKey('AuthSource', db_column='source', default=1, related_name='group')

    def __unicode__(self):
        return self.source.name


class AuthSource(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'auth_sources'


class Permission(models.Model):
    permission = models.CharField(max_length=8, primary_key=True, db_column='id')
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.permission, self.name)

    class Meta:
        db_table = 'permissions'


# class UserToGroup(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='uid', related_name='user_groups')
#     group = models.ForeignKey('Group', db_column='gid', related_name='user_groups')
#     permissions = models.ForeignKey('Permission', db_column='permissions', related_name='user_groups_permissions')
#     host_permissions = models.ForeignKey('Permission', db_column='host_permissions', related_name='user_groups_host_permissions')
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     objects = UserToGroupManager()

#     def __unicode__(self):
#         return '%s - %s' % (self.group.name, self.user.username)

#     class Meta:
#         db_table = 'users_to_groups'
#         managed = False


# class Group(models.Model):
#     name = models.TextField(unique=True, blank=True)
#     description = models.TextField(blank=True)
#     domains = models.ManyToManyField('dns.Domain', through='DomainToGroup', related_name='domain_groups')
#     hosts = models.ManyToManyField('hosts.Host', through='HostToGroup', related_name='host_groups')
#     networks = models.ManyToManyField('network.Network', through='NetworkToGroup', related_name='network_groups')
#     pools = models.ManyToManyField('network.Pool', through='PoolToGroup', related_name='pool_groups')
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     def __unicode__(self):
#         return self.name

#     class Meta:
#         db_table = 'groups'
#         managed = False


# class DomainToGroup(models.Model):
#     domain = models.ForeignKey('dns.Domain', db_column='did')
#     group = models.ForeignKey('Group', db_column='gid')
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     class Meta:
#         db_table = 'domains_to_groups'
#         managed = False


# class HostToGroup(models.Model):
#     host = models.ForeignKey('hosts.Host', db_column='mac')
#     group = models.ForeignKey('Group', db_column='gid')
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     class Meta:
#         db_table = 'hosts_to_groups'
#         managed = False


# class NetworkToGroup(models.Model):
#     network = models.ForeignKey('network.Network', db_column='nid')
#     group = models.ForeignKey('Group', db_column='gid')
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     class Meta:
#         db_table = 'networks_to_groups'
#         managed = False


# class PoolToGroup(models.Model):
#     pool = models.ForeignKey('network.Pool', db_column='pool')
#     group = models.ForeignKey('Group', db_column='gid')

#     class Meta:
#         db_table = 'pools_to_groups'
#         managed = False


# class InternalAuth(models.Model):
#     id = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True,
#                            db_column='id', related_name='internal_user')
#     password = models.CharField(max_length=128, db_column='hash')
#     name = models.CharField(max_length=255, blank=True)
#     email = models.CharField(max_length=255, blank=True)
#     changed = models.DateTimeField(auto_now=True)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

#     class Meta:
#         db_table = 'internal_auth'
#         managed = False


# Connect signals
pre_save.connect(force_usernames_uppercase, sender=User)
post_save.connect(assign_ipam_groups, sender=User)
pre_delete.connect(remove_obj_perms_connected_with_user, sender=User)
post_save.connect(add_group_souce, sender=AuthGroup)
