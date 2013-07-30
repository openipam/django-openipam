from django.db import models
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup, UserManager
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save, pre_delete
from django.db.models import Q
from django.conf import settings
from django.core.validators import ValidationError
from guardian.models import UserObjectPermission, GroupObjectPermission


class AuthSource(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'auth_sources'


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    source = models.ForeignKey('AuthSource', db_column='source')
    min_permissions = models.ForeignKey('Permission', db_column='min_permissions')
    # groups = models.ManyToManyField('Group', through='UserToGroup', related_name='users')

    def __unicode__(self):
        return self.username

    def get_auth_user(self):
        try:
            return AuthUser.objects.get(username=self.username)
        except AuthUser.DoesNotExist:
            return None

    class Meta:
        db_table = 'users'


class Permission(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'permissions'


class UserToGroup(models.Model):
    uid = models.ForeignKey('User', db_column='uid', related_name='user_groups')
    gid = models.ForeignKey('Group', db_column='gid', related_name='group_users')
    permissions = models.ForeignKey('Permission', db_column='permissions', related_name='default_permissions')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')
    host_permissions = models.ForeignKey('Permission', db_column='host_permissions', related_name='user_host_permissions')

    class Meta:
        db_table = 'users_to_groups'


class Group(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True, blank=True)
    description = models.TextField(blank=True)
    domains = models.ManyToManyField('dns.Domain', through='DomainToGroup', related_name='domain_groups')
    hosts = models.ManyToManyField('hosts.Host', through='HostToGroup', related_name='host_groups')
    networks = models.ManyToManyField('network.Network', through='NetworkToGroup', related_name='network_groups')
    pools = models.ManyToManyField('network.Pool', through='PoolToGroup', related_name='pool_groups')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'groups'


class DomainToGroup(models.Model):
    did = models.ForeignKey('dns.Domain', db_column='did')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')

    class Meta:
        db_table = 'domains_to_groups'


class HostToGroup(models.Model):
    mac = models.ForeignKey('hosts.Host', db_column='mac')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')

    class Meta:
        db_table = 'hosts_to_groups'


class NetworkToGroup(models.Model):
    nid = models.ForeignKey('network.Network', db_column='nid')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')

    class Meta:
        db_table = 'networks_to_groups'


class PoolToGroup(models.Model):
    pool = models.ForeignKey('network.Pool', db_column='pool')
    gid = models.ForeignKey('Group', db_column='gid')

    class Meta:
        db_table = 'pools_to_groups'


class InternalAuth(models.Model):
    id = models.ForeignKey('User', primary_key=True, db_column='id', related_name='internal_user')
    hash = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')

    class Meta:
        db_table = 'internal_auth'


# Force Usernames to be lower case when being created
def force_usernames_lowercase(sender, instance, **kwargs):
    instance.username = instance.username.lower()
pre_save.connect(force_usernames_lowercase, sender=AuthUser)


# Automatically assign new users to IPAM_USER_GROUP
def assign_ipam_groups(sender, instance, created, **kwargs):
    # Get user group
    ipam_user_group = AuthGroup.objects.get_or_create(name=settings.IPAM_USER_GROUP)[0]
    # Check to make sure Admin Group exists
    ipam_admin_group = AuthGroup.objects.get_or_create(name=settings.IPAM_ADMIN_GROUP)[0]

    if created:
        instance.groups.add(ipam_user_group)
post_save.connect(assign_ipam_groups, sender=AuthUser)


# Automatically remove permissions when user is deleted.
def remove_obj_perms_connected_with_user(sender, instance, **kwargs):
    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()
pre_delete.connect(remove_obj_perms_connected_with_user, sender=AuthUser)
