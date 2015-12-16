# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class LogBase(models.Model):
    id = models.IntegerField()  # not a primary key
    trigger_mode = models.CharField(max_length=10)
    trigger_tuple = models.CharField(max_length=5)
    trigger_changed = models.DateTimeField()
    trigger_id = models.BigIntegerField(primary_key=True)
    trigger_user = models.CharField(max_length=32)

    class Meta:
        abstract = True


class ChainPatternBase(models.Model):
    pattern = models.CharField(unique=True, max_length=64)
    description = models.CharField(max_length=2048, blank=True, null=True)

    def __unicode__(self):
        return self.pattern

    class Meta:
        abstract = True


class ChainPattern(ChainPatternBase):
    class Meta:
        managed = False
        db_table = 'chain_patterns'


class ChainPatternLog(LogBase, ChainPatternBase):
    class Meta:
        managed = False
        db_table = 'chain_patterns_log'


class ChainBase(models.Model):
    name = models.CharField(max_length=24)
    tbl = models.ForeignKey('Tables', db_column='tbl', blank=True, null=True)
    builtin = models.BooleanField(default=False)
    description = models.CharField(max_length=2048, blank=True, null=True)

    def __unicode__(self):
        if self.tbl:
            return "%s|%s" % (self.tbl, self.name)
        return self.name

    class Meta:
        abstract = True


class Chain(ChainBase):
    class Meta:
        managed = False
        db_table = 'chains'
        unique_together = (('name', 'tbl'),)


class ChainLog(LogBase, ChainBase):
    class Meta:
        managed = False
        db_table = 'chains_log'


class FirewallBase(models.Model):
    name = models.CharField(unique=True, max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Firewall(FirewallBase):
    class Meta:
        managed = False
        db_table = 'firewalls'


class FirewallLog(LogBase, FirewallBase):
    class Meta:
        managed = False
        db_table = 'firewalls_log'


class FirewallToChainPatternBase(models.Model):
    fw = models.ForeignKey(Firewall, db_column='fw')
    pat = models.ForeignKey(ChainPattern, db_column='pat')

    def __unicode__(self):
        return "%s(%s)" % (self.fw.name, self.pat.pattern)

    class Meta:
        abstract = True


class FirewallToChainPattern(FirewallToChainPatternBase):
    class Meta:
        managed = False
        db_table = 'firewalls_to_chain_patterns'
        unique_together = (('fw', 'pat'),)


class FirewallToChainPatternLog(LogBase, FirewallToChainPatternBase):
    class Meta:
        managed = False
        db_table = 'firewalls_to_chain_patterns_log'


class HostBase(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    host = models.TextField(unique=True, blank=True, null=True)  # This field type is a guess.
    owner = models.ForeignKey('Users', db_column='owner')
    description = models.CharField(max_length=2048, blank=True, null=True)
    host_end = models.TextField(blank=True, null=True)  # This field type is a guess.
    is_group = models.BooleanField(default=False)
    last_check = models.DateTimeField()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Host(HostBase):
    class Meta:
        managed = False
        db_table = 'hosts'
        unique_together = (('host', 'host_end'),)


class HostLog(LogBase, HostBase):
    class Meta:
        managed = False
        db_table = 'hosts_log'


class HostToGroupBase(models.Model):
    gid = models.ForeignKey(Host, db_column='gid', related_name="%(class)s_groups")
    hid = models.ForeignKey(Host, db_column='hid', related_name="%(class)s_hosts")
    expires = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "%s(%s)" % (self.gid.name, self.hid.name)

    class Meta:
        abstract = True


class HostToGroup(HostToGroupBase):
    class Meta:
        managed = False
        db_table = 'hosts_to_groups'
        unique_together = (('hid', 'gid'),)


class HostToGroupLog(LogBase, HostToGroupBase):
    class Meta:
        managed = False
        db_table = 'hosts_to_groups_log'


class InterfaceBase(models.Model):
    name = models.CharField(unique=True, max_length=32)
    description = models.CharField(max_length=2048, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Interface(InterfaceBase):
    class Meta:
        managed = False
        db_table = 'interfaces'


class InterfaceLog(LogBase, InterfaceBase):
    class Meta:
        managed = False
        db_table = 'interfaces_log'


class PortBase(models.Model):
    name = models.CharField(unique=True, max_length=32, blank=True, null=True)
    port = models.IntegerField()
    endport = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        abstract = True


class Port(PortBase):
    class Meta:
        managed = False
        db_table = 'ports'


class PortLog(LogBase, PortBase):
    class Meta:
        managed = False
        db_table = 'ports_log'


class ProtosBase(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        abstract = True


class Protos(ProtosBase):
    class Meta:
        managed = False
        db_table = 'protos'


class ProtosLog(LogBase, ProtosBase):
    class Meta:
        managed = False
        db_table = 'protos_log'


class RealInterfaceBase(models.Model):
    name = models.CharField(max_length=32)
    pseudo = models.ForeignKey(Interface, db_column='pseudo')
    is_bridged = models.BooleanField(default=False)
    firewall = models.ForeignKey(Firewall)

    class Meta:
        abstract = True


class RealInterface(RealInterfaceBase):
    class Meta:
        managed = False
        db_table = 'real_interfaces'


class RealInterfaceLog(LogBase, RealInterfaceBase):
    class Meta:
        managed = False
        db_table = 'real_interfaces_log'


class RuleStats(models.Model):
    id = models.BigIntegerField(primary_key=True)
    rule = models.ForeignKey('Rule', db_column='rule')
    packets = models.BigIntegerField()
    bytes = models.BigIntegerField()
    time = models.DateTimeField()
    src = models.ForeignKey(Host, db_column='src', blank=True, null=True, related_name='%(class)s_src')
    dst = models.ForeignKey(Host, db_column='dst', blank=True, null=True, related_name='%(class)s_dst')

    class Meta:
        managed = False
        db_table = 'rule_stats'


class RuleBase(models.Model):
    chain = models.ForeignKey(Chain, db_column='chain', related_name='%(class)s_chain')
    if_in = models.ForeignKey(Interface, db_column='if_in', blank=True, null=True, related_name='%(class)s_if_in')
    if_out = models.ForeignKey(Interface, db_column='if_out', blank=True, null=True, related_name='%(class)s_if_out')
    proto = models.ForeignKey(Protos, db_column='proto', blank=True, null=True)
    src = models.ForeignKey(Host, db_column='src', blank=True, null=True, related_name='%(class)s_src')
    sport = models.ForeignKey(Port, db_column='sport', blank=True, null=True, related_name='%(class)s_sport')
    dst = models.ForeignKey(Host, db_column='dst', blank=True, null=True, related_name='%(class)s_dst')
    dport = models.ForeignKey(Port, db_column='dport', blank=True, null=True, related_name='%(class)s_dport')
    target = models.ForeignKey(Chain, db_column='target', related_name='%(class)s_target')
    additional = models.CharField(max_length=2048, blank=True, null=True)
    ord = models.IntegerField()
    enabled = models.BooleanField(default=False)
    description = models.CharField(max_length=2048, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    created_for = models.ForeignKey('Users', db_column='created_for')

    class Meta:
        abstract = True


class Rule(RuleBase):
    class Meta:
        managed = False
        db_table = 'rules'


class RuleLog(LogBase, RuleBase):
    class Meta:
        managed = False
        db_table = 'rules_log'


class TablesBase(models.Model):
    name = models.CharField(unique=True, max_length=32)
    description = models.CharField(max_length=2048, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Tables(TablesBase):
    class Meta:
        managed = False
        db_table = 'tables'


class TablesLog(LogBase, TablesBase):
    class Meta:
        managed = False
        db_table = 'tables_log'


class UsersBase(models.Model):
    name = models.CharField(unique=True, max_length=128)
    email = models.CharField(max_length=512, blank=True, null=True)
    a_number = models.CharField(max_length=9, blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.a_number, self.name)

    class Meta:
        abstract = True


class Users(UsersBase):
    class Meta:
        managed = False
        db_table = 'users'


class UsersLog(LogBase, UsersBase):
    class Meta:
        managed = False
        db_table = 'users_log'
