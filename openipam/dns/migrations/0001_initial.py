# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

	def forwards(self, orm):
		# Adding model 'Domain'
		db.create_table('domains', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
			('master', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
			('last_check', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
			('type', self.gf('django.db.models.fields.CharField')(max_length=6)),
			('notified_serial', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
			('account', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'dns', ['Domain'])

		# Adding model 'DnsRecord'
		db.create_table('dns_records', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('did', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.Domain'], db_column='did')),
			('tid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.DnsType'], db_column='tid')),
			('vid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.DnsView'], null=True, db_column='vid', blank=True)),
			('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
			('text_content', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
			('ip_content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Address'], null=True, db_column='ip_content', blank=True)),
			('ttl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
			('priority', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'dns', ['DnsRecord'])

		# Adding model 'DhcpDnsRecord'
		db.create_table('dhcp_dns_records', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('did', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.Domain'], db_column='did')),
			('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], unique=True, db_column='name')),
			('ip_content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Address'], null=True, db_column='ip_content', blank=True)),
			('ttl', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
		))
		db.send_create_signal(u'dns', ['DhcpDnsRecord'])

		# Adding model 'DnsType'
		db.create_table('dns_types', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('name', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
			('min_permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Permission'], db_column='min_permissions')),
		))
		db.send_create_signal(u'dns', ['DnsType'])

		# Adding model 'DnsView'
		db.create_table('dns_views', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
		))
		db.send_create_signal(u'dns', ['DnsView'])

		# Adding model 'Supermaster'
		db.create_table('supermasters', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('ip', self.gf('django.db.models.fields.CharField')(max_length=25)),
			('nameserver', self.gf('django.db.models.fields.CharField')(max_length=255)),
			('account', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'dns', ['Supermaster'])


	def backwards(self, orm):
		# Deleting model 'Domain'
		db.delete_table('domains')

		# Deleting model 'DnsRecord'
		db.delete_table('dns_records')

		# Deleting model 'DhcpDnsRecord'
		db.delete_table('dhcp_dns_records')

		# Deleting model 'DnsType'
		db.delete_table('dns_types')

		# Deleting model 'DnsView'
		db.delete_table('dns_views')

		# Deleting model 'Supermaster'
		db.delete_table('supermasters')


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
		u'auth.user': {
			'Meta': {'object_name': 'User'},
			'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
			'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
			'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
			'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
			'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
			'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
			'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
			'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
			'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
		},
		u'contenttypes.contenttype': {
			'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
			'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
		},
		u'dns.dhcpdnsrecord': {
			'Meta': {'object_name': 'DhcpDnsRecord', 'db_table': "'dhcp_dns_records'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'did': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']", 'db_column': "'did'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'ip_content': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Address']", 'null': 'True', 'db_column': "'ip_content'", 'blank': 'True'}),
			'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'unique': 'True', 'db_column': "'name'"}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
		},
		u'dns.dnsrecord': {
			'Meta': {'object_name': 'DnsRecord', 'db_table': "'dns_records'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'did': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']", 'db_column': "'did'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'ip_content': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Address']", 'null': 'True', 'db_column': "'ip_content'", 'blank': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
			'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'text_content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'tid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.DnsType']", 'db_column': "'tid'"}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'vid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.DnsView']", 'null': 'True', 'db_column': "'vid'", 'blank': 'True'})
		},
		u'dns.dnsrecordmunged': {
			'Meta': {'object_name': 'DnsRecordMunged', 'db_table': "'dns_records_munged'", 'managed': 'False'},
			'change_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'domain_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'prio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
			'view_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
		},
		u'dns.dnstype': {
			'Meta': {'object_name': 'DnsType', 'db_table': "'dns_types'"},
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
		},
		u'dns.dnsview': {
			'Meta': {'object_name': 'DnsView', 'db_table': "'dns_views'"},
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
		},
		u'dns.domain': {
			'Meta': {'object_name': 'Domain', 'db_table': "'domains'"},
			'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
			'notified_serial': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
		},
		u'dns.pdnszonexfer': {
			'Meta': {'object_name': 'PdnsZoneXfer', 'db_table': "'pdns_zone_xfer'", 'managed': 'False'},
			'change_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
			'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
			'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
		},
		u'dns.record': {
			'Meta': {'object_name': 'Record', 'db_table': "'records'", 'managed': 'False'},
			'change_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'domain_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'prio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
			'view_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
		},
		u'dns.recordmunged': {
			'Meta': {'object_name': 'RecordMunged', 'db_table': "'records_munged'", 'managed': 'False'},
			'change_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'domain_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'prio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'view_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
		},
		u'dns.supermaster': {
			'Meta': {'object_name': 'Supermaster', 'db_table': "'supermasters'"},
			'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
			'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
		},
		u'hosts.host': {
			'Meta': {'object_name': 'Host', 'db_table': "'hosts'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
			'expires': ('django.db.models.fields.DateTimeField', [], {}),
			'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
			'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'})
		},
		u'network.address': {
			'Meta': {'object_name': 'Address', 'db_table': "'addresses'"},
			'address': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'primary_key': 'True'}),
			'changed': ('django.db.models.fields.DateTimeField', [], {}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'null': 'True', 'db_column': "'mac'", 'blank': 'True'}),
			'network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Network']", 'db_column': "'network'"}),
			'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']", 'null': 'True', 'db_column': "'pool'", 'blank': 'True'}),
			'reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
		},
		u'network.dhcpgroup': {
			'Meta': {'ordering': "('name',)", 'object_name': 'DhcpGroup', 'db_table': "'dhcp_groups'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
		},
		u'network.network': {
			'Meta': {'object_name': 'Network', 'db_table': "'networks'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
			'gateway': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'network': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'primary_key': 'True'}),
			'shared_network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.SharedNetwork']", 'null': 'True', 'db_column': "'shared_network'", 'blank': 'True'})
		},
		u'network.pool': {
			'Meta': {'object_name': 'Pool', 'db_table': "'pools'"},
			'allow_unknown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'lease_time': ('django.db.models.fields.IntegerField', [], {}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
		},
		u'network.sharednetwork': {
			'Meta': {'object_name': 'SharedNetwork', 'db_table': "'shared_networks'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
		},
		u'user.authsource': {
			'Meta': {'object_name': 'AuthSource', 'db_table': "'auth_sources'"},
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'})
		},
		u'user.permission': {
			'Meta': {'object_name': 'Permission', 'db_table': "'permissions'"},
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.TextField', [], {'blank': 'True'})
		},
		u'user.user': {
			'Meta': {'object_name': 'User', 'db_table': "'users'"},
			'auth_user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
			'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.AuthSource']", 'db_column': "'source'"}),
			'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
		}
	}

	complete_apps = ['dns']
