# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

	def forwards(self, orm):
		# Adding model 'Attribute'
		db.create_table('attributes', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
			('structured', self.gf('django.db.models.fields.BooleanField')(default=False)),
			('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
			('validation', self.gf('django.db.models.fields.TextField')(blank=True)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'hosts', ['Attribute'])

		# Adding model 'Disabled'
		db.create_table('disabled', (
			('mac', self.gf('netfields.fields.MACAddressField')(max_length=17, primary_key=True)),
			('reason', self.gf('django.db.models.fields.TextField')(blank=True)),
			('disabled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('disabled_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='disabled_by')),
		))
		db.send_create_signal(u'hosts', ['Disabled'])

		# Adding model 'ExpirationType'
		db.create_table('expiration_types', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('expiration', self.gf('django.db.models.fields.TextField')(blank=True)),
			('min_permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Permission'], db_column='min_permissions')),
		))
		db.send_create_signal(u'hosts', ['ExpirationType'])

		# Adding model 'FreeformAttributeToHost'
		db.create_table('freeform_attributes_to_hosts', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('mac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], db_column='mac')),
			('aid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Attribute'], db_column='aid')),
			('value', self.gf('django.db.models.fields.TextField')()),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'hosts', ['FreeformAttributeToHost'])

		# Adding model 'GuestTicket'
		db.create_table('guest_tickets', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('uid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='uid')),
			('ticket', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
			('starts', self.gf('django.db.models.fields.DateTimeField')()),
			('ends', self.gf('django.db.models.fields.DateTimeField')()),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
		))
		db.send_create_signal(u'hosts', ['GuestTicket'])

		# Adding model 'GulRecentArpByaddress'
		db.create_table('gul_recent_arp_byaddress', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('mac', self.gf('netfields.fields.MACAddressField')(max_length=17, blank=True)),
			('address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
			('stopstamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
		))
		db.send_create_signal(u'hosts', ['GulRecentArpByaddress'])

		# Adding model 'GulRecentArpBymac'
		db.create_table('gul_recent_arp_bymac', (
			(u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
			('mac', self.gf('netfields.fields.MACAddressField')(max_length=17, blank=True)),
			('address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
			('stopstamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
		))
		db.send_create_signal(u'hosts', ['GulRecentArpBymac'])

		# Adding model 'Host'
		db.create_table('hosts', (
			('mac', self.gf('netfields.fields.MACAddressField')(max_length=17, primary_key=True)),
			('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
			('description', self.gf('django.db.models.fields.TextField')(blank=True)),
			('dhcp_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.DhcpGroup'], null=True, db_column='dhcp_group', blank=True)),
			('expires', self.gf('django.db.models.fields.DateTimeField')()),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'hosts', ['Host'])

		# Adding model 'MacOui'
		db.create_table('mac_oui', (
			('oui', self.gf('netfields.fields.MACAddressField')(max_length=17, primary_key=True)),
			('vendor', self.gf('django.db.models.fields.TextField')()),
		))
		db.send_create_signal(u'hosts', ['MacOui'])

		# Adding model 'Notification'
		db.create_table('notifications', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('notification', self.gf('django.db.models.fields.TextField')(blank=True)),
			('min_permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Permission'], db_column='min_permissions')),
		))
		db.send_create_signal(u'hosts', ['Notification'])

		# Adding model 'NotificationToHost'
		db.create_table('notifications_to_hosts', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('nid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Notification'], db_column='nid')),
			('mac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], db_column='mac')),
		))
		db.send_create_signal(u'hosts', ['NotificationToHost'])

		# Adding model 'StructuredAttributeValue'
		db.create_table('structured_attribute_values', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('aid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Attribute'], db_column='aid')),
			('value', self.gf('django.db.models.fields.TextField')()),
			('is_default', self.gf('django.db.models.fields.BooleanField')(default=False)),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'hosts', ['StructuredAttributeValue'])

		# Adding model 'StructuredAttributeToHost'
		db.create_table('structured_attributes_to_hosts', (
			('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
			('mac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], db_column='mac')),
			('avid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.StructuredAttributeValue'], db_column='avid')),
			('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
			('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
		))
		db.send_create_signal(u'hosts', ['StructuredAttributeToHost'])


	def backwards(self, orm):
		# Deleting model 'Attribute'
		db.delete_table('attributes')

		# Deleting model 'Disabled'
		db.delete_table('disabled')

		# Deleting model 'ExpirationType'
		db.delete_table('expiration_types')

		# Deleting model 'FreeformAttributeToHost'
		db.delete_table('freeform_attributes_to_hosts')

		# Deleting model 'GuestTicket'
		db.delete_table('guest_tickets')

		# Deleting model 'GulRecentArpByaddress'
		db.delete_table('gul_recent_arp_byaddress')

		# Deleting model 'GulRecentArpBymac'
		db.delete_table('gul_recent_arp_bymac')

		# Deleting model 'Host'
		db.delete_table('hosts')

		# Deleting model 'MacOui'
		db.delete_table('mac_oui')

		# Deleting model 'Notification'
		db.delete_table('notifications')

		# Deleting model 'NotificationToHost'
		db.delete_table('notifications_to_hosts')

		# Deleting model 'StructuredAttributeValue'
		db.delete_table('structured_attribute_values')

		# Deleting model 'StructuredAttributeToHost'
		db.delete_table('structured_attributes_to_hosts')


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
		u'hosts.attribute': {
			'Meta': {'object_name': 'Attribute', 'db_table': "'attributes'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
			'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'structured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'validation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
		},
		u'hosts.attributetohost': {
			'Meta': {'object_name': 'AttributeToHost', 'db_table': "'attributes_to_hosts'", 'managed': 'False'},
			'aid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			'avid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'blank': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
			'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'structured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
		},
		u'hosts.disabled': {
			'Meta': {'object_name': 'Disabled', 'db_table': "'disabled'"},
			'disabled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'disabled_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'disabled_by'"}),
			'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'}),
			'reason': ('django.db.models.fields.TextField', [], {'blank': 'True'})
		},
		u'hosts.expirationtype': {
			'Meta': {'object_name': 'ExpirationType', 'db_table': "'expiration_types'"},
			'expiration': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"})
		},
		u'hosts.freeformattributetohost': {
			'Meta': {'object_name': 'FreeformAttributeToHost', 'db_table': "'freeform_attributes_to_hosts'"},
			'aid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Attribute']", 'db_column': "'aid'"}),
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
			'value': ('django.db.models.fields.TextField', [], {})
		},
		u'hosts.guestticket': {
			'Meta': {'object_name': 'GuestTicket', 'db_table': "'guest_tickets'"},
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'ends': ('django.db.models.fields.DateTimeField', [], {}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'starts': ('django.db.models.fields.DateTimeField', [], {}),
			'ticket': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
			'uid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'uid'"})
		},
		u'hosts.gulrecentarpbyaddress': {
			'Meta': {'object_name': 'GulRecentArpByaddress', 'db_table': "'gul_recent_arp_byaddress'"},
			'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'blank': 'True'}),
			'stopstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
		},
		u'hosts.gulrecentarpbymac': {
			'Meta': {'object_name': 'GulRecentArpBymac', 'db_table': "'gul_recent_arp_bymac'"},
			'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
			u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
			'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'blank': 'True'}),
			'stopstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
		u'hosts.macoui': {
			'Meta': {'object_name': 'MacOui', 'db_table': "'mac_oui'"},
			'oui': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'}),
			'vendor': ('django.db.models.fields.TextField', [], {})
		},
		u'hosts.notification': {
			'Meta': {'object_name': 'Notification', 'db_table': "'notifications'"},
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
			'notification': ('django.db.models.fields.TextField', [], {'blank': 'True'})
		},
		u'hosts.notificationtohost': {
			'Meta': {'object_name': 'NotificationToHost', 'db_table': "'notifications_to_hosts'"},
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
			'nid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Notification']", 'db_column': "'nid'"})
		},
		u'hosts.structuredattributetohost': {
			'Meta': {'object_name': 'StructuredAttributeToHost', 'db_table': "'structured_attributes_to_hosts'"},
			'avid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.StructuredAttributeValue']", 'db_column': "'avid'"}),
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"})
		},
		u'hosts.structuredattributevalue': {
			'Meta': {'object_name': 'StructuredAttributeValue', 'db_table': "'structured_attribute_values'"},
			'aid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Attribute']", 'db_column': "'aid'"}),
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
			'value': ('django.db.models.fields.TextField', [], {})
		},
		u'network.dhcpgroup': {
			'Meta': {'ordering': "('name',)", 'object_name': 'DhcpGroup', 'db_table': "'dhcp_groups'"},
			'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
			'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
			'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
			'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
			'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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

	complete_apps = ['hosts']
