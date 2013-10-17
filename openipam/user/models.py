from django.db import models
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, UserManager
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.http import urlquote
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.conf import settings
from django.core.validators import ValidationError
from django_postgres import BitStringField


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
    is_ipamadmin = models.BooleanField(_('ipam administrator'), default=False,
        help_text=_('Designates whether this user has IPAM admin privledges'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    min_permissions = models.ForeignKey('Permission', db_column='min_permissions', related_name='user_min_permissions')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.username

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

    def get_ipam_groups(self):
        return Group.objects.filter(group_users__user=self)

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Permission(models.Model):
    permission = BitStringField(max_length=8, primary_key=True, db_column='id')
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.permission.bin, self.name)

    class Meta:
        db_table = 'permissions'
        managed = False


class UserToGroupManager(models.Manager):

    def get_queryset(self):
        return super(UserToGroupManager, self).get_queryset().select_related().all()


class UserToGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='uid', related_name='user_groups')
    group = models.ForeignKey('Group', db_column='gid', related_name='group_users')
    permissions = models.ForeignKey('Permission', db_column='permissions', related_name='default_permissions')
    host_permissions = models.ForeignKey('Permission', db_column='host_permissions', related_name='user_host_permissions')
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    objects = UserToGroupManager()

    def __unicode__(self):
        return self.gid.name

    class Meta:
        db_table = 'users_to_groups'
        managed = False


class Group(models.Model):
    name = models.TextField(unique=True, blank=True)
    description = models.TextField(blank=True)
    domains = models.ManyToManyField('dns.Domain', through='DomainToGroup', related_name='domain_groups')
    hosts = models.ManyToManyField('hosts.Host', through='HostToGroup', related_name='host_groups')
    networks = models.ManyToManyField('network.Network', through='NetworkToGroup', related_name='network_groups')
    pools = models.ManyToManyField('network.Pool', through='PoolToGroup', related_name='pool_groups')
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'groups'
        managed = False


class DomainToGroup(models.Model):
    domain = models.ForeignKey('dns.Domain', db_column='did')
    group = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    class Meta:
        db_table = 'domains_to_groups'
        managed = False


class HostToGroup(models.Model):
    mac = models.ForeignKey('hosts.Host', db_column='mac')
    group = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    class Meta:
        db_table = 'hosts_to_groups'
        managed = False


class NetworkToGroup(models.Model):
    network = models.ForeignKey('network.Network', db_column='nid')
    group = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    class Meta:
        db_table = 'networks_to_groups'
        managed = False


class PoolToGroup(models.Model):
    pool = models.ForeignKey('network.Pool', db_column='pool')
    group = models.ForeignKey('Group', db_column='gid')

    class Meta:
        db_table = 'pools_to_groups'
        managed = False


class InternalAuth(models.Model):
    id = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True, db_column='id', related_name='internal_user')
    hash = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='changed_by')

    class Meta:
        db_table = 'internal_auth'
        managed = False


# Force Usernames to be lower case when being created
def force_usernames_uppercase(sender, instance, **kwargs):
    username = instance.username.lower()
    if username.startswith('a') and username[1:].isdigit() and len(username) == 9:
        instance.username = instance.username.upper()
pre_save.connect(force_usernames_uppercase, sender=User)


# Automatically assign new users to IPAM_USER_GROUP
def assign_ipam_groups(sender, instance, created, **kwargs):
    # Get user group
    ipam_user_group = AuthGroup.objects.get_or_create(name=settings.IPAM_USER_GROUP)[0]
    # Check to make sure Admin Group exists
    ipam_admin_group = AuthGroup.objects.get_or_create(name=settings.IPAM_ADMIN_GROUP)[0]

    if created:
        instance.groups.add(ipam_user_group)
post_save.connect(assign_ipam_groups, sender=User)


# Automatically remove permissions when user is deleted.
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    from guardian.models import UserObjectPermission, GroupObjectPermission

    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()
pre_delete.connect(remove_obj_perms_connected_with_user, sender=User)



try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^django_postgres\.bitstrings\.BitStringField",
    ])
except ImportError:
    pass

