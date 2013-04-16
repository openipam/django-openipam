from django.db import models


class AuthSource(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, blank=True)
    class Meta:
        db_table = 'auth_sources'


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    source = models.ForeignKey('AuthSource', db_column='source')
    min_permissions = models.ForeignKey('Permission', db_column='min_permissions')
    class Meta:
        db_table = 'users'


class Permission(models.Model):
    id = models.TextField(primary_key=True) # This field type is a guess.
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'permissions'


class UserToGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.ForeignKey('User', db_column='uid', related_name='user_groups')
    gid = models.ForeignKey('Group', db_column='gid', related_name='group_users')
    permissions = models.ForeignKey('Permission', db_column='permissions', related_name='user_permissions')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')
    host_permissions = models.ForeignKey('Permission', db_column='host_permissions', related_name='user_host_permissions')
    class Meta:
        db_table = 'users_to_groups'


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('User', db_column='changed_by')
    class Meta:
        db_table = 'groups'


class DomainToGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    did = models.ForeignKey('dns.Domain', db_column='did')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')
    class Meta:
        db_table = 'domains_to_groups'


class HostToGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    mac = models.ForeignKey('host.Host', db_column='mac')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')
    class Meta:
        db_table = 'hosts_to_groups'


class NetworkToGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    nid = models.ForeignKey('network.Network', db_column='nid')
    gid = models.ForeignKey('Group', db_column='gid')
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('User', db_column='changed_by')
    class Meta:
        db_table = 'networks_to_groups'


class PoolToGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    pool = models.ForeignKey('network.Pool', db_column='pool')
    gid = models.ForeignKey('Group', db_column='gid')
    class Meta:
        db_table = 'pools_to_groups'


class InternalAuth(models.Model):
    id = models.ForeignKey('User', primary_key=True, db_column='id', related_name='internal_user')
    hash = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    changed = models.DateTimeField()
    changed_by = models.ForeignKey('User', db_column='changed_by')
    class Meta:
        db_table = 'internal_auth'
