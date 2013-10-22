# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from bitstring import Bits


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lease'
        db.create_table('leases', (
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Address'], primary_key=True, db_column='address')),
            ('mac', self.gf('netfields.fields.MACAddressField')(max_length=17, unique=True, null=True, blank=True)),
            ('abandoned', self.gf('django.db.models.fields.BooleanField')()),
            ('server', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('starts', self.gf('django.db.models.fields.DateTimeField')()),
            ('ends', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'network', ['Lease'])

        # Adding model 'Pool'
        db.create_table('pools', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('allow_unknown', self.gf('django.db.models.fields.BooleanField')()),
            ('lease_time', self.gf('django.db.models.fields.IntegerField')()),
            ('dhcp_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.DhcpGroup'], null=True, db_column='dhcp_group', blank=True)),
        ))
        db.send_create_signal(u'network', ['Pool'])

        # Adding model 'DhcpGroup'
        db.create_table('dhcp_groups', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['DhcpGroup'])

        # Adding model 'DhcpOption'
        db.create_table('dhcp_options', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True, blank=True)),
            ('option', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'network', ['DhcpOption'])

        # Adding model 'DhcpOptionToDhcpGroup'
        db.create_table('dhcp_options_to_dhcp_groups', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='option_values', null=True, db_column='gid', to=orm['network.DhcpGroup'])),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='group_values', null=True, db_column='oid', to=orm['network.DhcpOption'])),
            ('value', self.gf('django.db.models.fields.BinaryField')(null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['DhcpOptionToDhcpGroup'])

        # Adding model 'HostToPool'
        db.create_table('hosts_to_pools', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], db_column='mac')),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Pool'])),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['HostToPool'])

        # Adding model 'SharedNetwork'
        db.create_table('shared_networks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['SharedNetwork'])

        # Adding model 'Network'
        db.create_table('networks', (
            ('network', self.gf('netfields.fields.CidrAddressField')(max_length=43, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('gateway', self.gf('netfields.fields.InetAddressField')(max_length=39, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('dhcp_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.DhcpGroup'], null=True, db_column='dhcp_group', blank=True)),
            ('shared_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.SharedNetwork'], null=True, db_column='shared_network', blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['Network'])

        # Adding model 'Vlan'
        db.create_table('vlans', (
            ('id', self.gf('django.db.models.fields.SmallIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['Vlan'])

        # Adding model 'NetworkToVlan'
        db.create_table('networks_to_vlans', (
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Network'], primary_key=True, db_column='network')),
            ('vlan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Vlan'], db_column='vlan')),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['NetworkToVlan'])

        # Adding model 'Address'
        db.create_table('addresses', (
            ('address', self.gf('netfields.fields.InetAddressField')(max_length=39, primary_key=True)),
            ('mac', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='addresses', null=True, db_column='mac', to=orm['hosts.Host'])),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Pool'], null=True, db_column='pool', blank=True)),
            ('reserved', self.gf('django.db.models.fields.BooleanField')()),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Network'], db_column='network')),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'network', ['Address'])


    def backwards(self, orm):
        # Deleting model 'Lease'
        db.delete_table('leases')

        # Deleting model 'Pool'
        db.delete_table('pools')

        # Deleting model 'DhcpGroup'
        db.delete_table('dhcp_groups')

        # Deleting model 'DhcpOption'
        db.delete_table('dhcp_options')

        # Deleting model 'DhcpOptionToDhcpGroup'
        db.delete_table('dhcp_options_to_dhcp_groups')

        # Deleting model 'HostToPool'
        db.delete_table('hosts_to_pools')

        # Deleting model 'SharedNetwork'
        db.delete_table('shared_networks')

        # Deleting model 'Network'
        db.delete_table('networks')

        # Deleting model 'Vlan'
        db.delete_table('vlans')

        # Deleting model 'NetworkToVlan'
        db.delete_table('networks_to_vlans')

        # Deleting model 'Address'
        db.delete_table('addresses')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hosts.host': {
            'Meta': {'ordering': "('hostname',)", 'object_name': 'Host', 'db_table': "'hosts'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pool_hosts'", 'to': u"orm['network.Pool']", 'through': u"orm['network.HostToPool']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'network.address': {
            'Meta': {'object_name': 'Address', 'db_table': "'addresses'"},
            'address': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'primary_key': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'addresses'", 'null': 'True', 'db_column': "'mac'", 'to': u"orm['hosts.Host']"}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Network']", 'db_column': "'network'"}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']", 'null': 'True', 'db_column': "'pool'", 'blank': 'True'}),
            'reserved': ('django.db.models.fields.BooleanField', [], {})
        },
        u'network.dhcpgroup': {
            'Meta': {'object_name': 'DhcpGroup', 'db_table': "'dhcp_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dhcp_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['network.DhcpOption']", 'through': u"orm['network.DhcpOptionToDhcpGroup']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'network.dhcpoption': {
            'Meta': {'object_name': 'DhcpOption', 'db_table': "'dhcp_options'"},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'option': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'network.dhcpoptiontodhcpgroup': {
            'Meta': {'object_name': 'DhcpOptionToDhcpGroup', 'db_table': "'dhcp_options_to_dhcp_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'option_values'", 'null': 'True', 'db_column': "'gid'", 'to': u"orm['network.DhcpGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'group_values'", 'null': 'True', 'db_column': "'oid'", 'to': u"orm['network.DhcpOption']"}),
            'value': ('django.db.models.fields.BinaryField', [], {'null': 'True', 'blank': 'True'})
        },
        u'network.hosttopool': {
            'Meta': {'object_name': 'HostToPool', 'db_table': "'hosts_to_pools'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']"})
        },
        u'network.lease': {
            'Meta': {'object_name': 'Lease', 'db_table': "'leases'"},
            'abandoned': ('django.db.models.fields.BooleanField', [], {}),
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Address']", 'primary_key': 'True', 'db_column': "'address'"}),
            'ends': ('django.db.models.fields.DateTimeField', [], {}),
            'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'starts': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'network.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'networks'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            'gateway': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'network': ('netfields.fields.CidrAddressField', [], {'max_length': '43', 'primary_key': 'True'}),
            'shared_network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.SharedNetwork']", 'null': 'True', 'db_column': "'shared_network'", 'blank': 'True'}),
            'vlans': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'vlan_networks'", 'symmetrical': 'False', 'through': u"orm['network.NetworkToVlan']", 'to': u"orm['network.Vlan']"})
        },
        u'network.networktovlan': {
            'Meta': {'object_name': 'NetworkToVlan', 'db_table': "'networks_to_vlans'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Network']", 'primary_key': 'True', 'db_column': "'network'"}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Vlan']", 'db_column': "'vlan'"})
        },
        u'network.pool': {
            'Meta': {'object_name': 'Pool', 'db_table': "'pools'"},
            'allow_unknown': ('django.db.models.fields.BooleanField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lease_time': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'network.sharednetwork': {
            'Meta': {'object_name': 'SharedNetwork', 'db_table': "'shared_networks'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'network.vlan': {
            'Meta': {'object_name': 'Vlan', 'db_table': "'vlans'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.SmallIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'user.permission': {
            'Meta': {'object_name': 'Permission', 'db_table': "'permissions'", 'managed': 'False'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'permission': ('django_postgres.bitstrings.BitStringField', [], {'default': "Bits('0x00')", 'max_length': '8', 'primary_key': 'True', 'db_column': "'id'"})
        },
        u'user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'users'"},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_ipamadmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_min_permissions'", 'db_column': "'min_permissions'", 'to': u"orm['user.Permission']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['network']
