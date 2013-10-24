# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from bitstring import Bits


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DefaultPool'
        db.create_table('default_pools', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pool_defaults', null=True, to=orm['network.Pool'])),
            ('cidr', self.gf('netfields.fields.CidrAddressField')(unique=True, max_length=43)),
        ))
        db.send_create_signal(u'network', ['DefaultPool'])

        # Adding model 'AddressType'
        db.create_table('addresstypes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Pool'], null=True, blank=True)),
            ('is_default', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'network', ['AddressType'])

        # Adding M2M table for field ranges on 'AddressType'
        m2m_table_name = db.shorten_name('addresstypes_ranges')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('addresstype', models.ForeignKey(orm[u'network.addresstype'], null=False)),
            ('networkrange', models.ForeignKey(orm[u'network.networkrange'], null=False))
        ))
        db.create_unique(m2m_table_name, ['addresstype_id', 'networkrange_id'])

        # Adding model 'NetworkRange'
        db.create_table('network_ranges', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('range', self.gf('netfields.fields.CidrAddressField')(unique=True, max_length=43)),
        ))
        db.send_create_signal(u'network', ['NetworkRange'])

        # Adding field 'Pool.assignable'
        db.add_column('pools', 'assignable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        try:
        # Adding field for pools_log
        db.add_column('pools_log', 'assignable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)
        except:
            pass


    def backwards(self, orm):
        # Deleting model 'DefaultPool'
        db.delete_table('default_pools')

        # Deleting model 'AddressType'
        db.delete_table('addresstypes')

        # Removing M2M table for field ranges on 'AddressType'
        db.delete_table(db.shorten_name('addresstypes_ranges'))

        # Deleting model 'NetworkRange'
        db.delete_table('network_ranges')

        # Deleting field 'Pool.assignable'
        db.delete_column('pools', 'assignable')

        try:
            # Deleting field for pools_log table
            db.delete_column('pools_log', 'assignable')
        except:
            pass


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
            'address_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.AddressType']", 'null': 'True', 'blank': 'True'}),
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
        u'network.addresstype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'AddressType', 'db_table': "'addresstypes'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']", 'null': 'True', 'blank': 'True'}),
            'ranges': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'address_ranges'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['network.NetworkRange']"})
        },
        u'network.defaultpool': {
            'Meta': {'object_name': 'DefaultPool', 'db_table': "'default_pools'"},
            'cidr': ('netfields.fields.CidrAddressField', [], {'unique': 'True', 'max_length': '43'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pool_defaults'", 'null': 'True', 'to': u"orm['network.Pool']"})
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
        u'network.networkrange': {
            'Meta': {'object_name': 'NetworkRange', 'db_table': "'network_ranges'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'range': ('netfields.fields.CidrAddressField', [], {'unique': 'True', 'max_length': '43'})
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
            'assignable': ('django.db.models.fields.BooleanField', [], {}),
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
