# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Host.address_type'
        db.add_column('hosts', 'address_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.AddressType'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Deleting field 'Host.address_type'
        db.delete_column('hosts', 'address_type_id')



    models = {
        u'hosts.attribute': {
            'Meta': {'object_name': 'Attribute', 'db_table': "'attributes'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"})
        },
        u'hosts.freeformattributetohost': {
            'Meta': {'object_name': 'FreeformAttributeToHost', 'db_table': "'freeform_attributes_to_hosts'"},
            'aid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Attribute']", 'db_column': "'aid'"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'hosts.guestticket': {
            'Meta': {'object_name': 'GuestTicket', 'db_table': "'guest_tickets'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ends': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starts': ('django.db.models.fields.DateTimeField', [], {}),
            'ticket': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'uid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'uid'"})
        },
        u'hosts.gulrecentarpbyaddress': {
            'Meta': {'object_name': 'GulRecentArpByaddress', 'db_table': "'gul_recent_arp_byaddress'"},
            'address': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'blank': 'True'}),
            'stopstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hosts.gulrecentarpbymac': {
            'Meta': {'object_name': 'GulRecentArpBymac', 'db_table': "'gul_recent_arp_bymac'"},
            'address': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'blank': 'True'}),
            'stopstamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hosts.host': {
            'Meta': {'object_name': 'Host', 'db_table': "'hosts'"},
            'address_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.AddressType']", 'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'freeform_attributes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'freeform_hosts'", 'symmetrical': 'False', 'through': u"orm['hosts.FreeformAttributeToHost']", 'to': u"orm['hosts.Attribute']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'mac': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pool_hosts'", 'symmetrical': 'False', 'through': u"orm['network.HostToPool']", 'to': u"orm['network.Pool']"}),
            'structured_attributes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'structured_hosts'", 'symmetrical': 'False', 'through': u"orm['hosts.StructuredAttributeToHost']", 'to': u"orm['hosts.StructuredAttributeValue']"})
        },
        u'hosts.macoui': {
            'Meta': {'object_name': 'MacOui', 'db_table': "'mac_oui'"},
            'oui': ('netfields.fields.MACAddressField', [], {'max_length': '17', 'primary_key': 'True'}),
            'vendor': ('django.db.models.fields.TextField', [], {})
        },
        u'hosts.notification': {
            'Meta': {'object_name': 'Notification', 'db_table': "'notifications'"},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'host_notifications'", 'symmetrical': 'False', 'through': u"orm['hosts.NotificationToHost']", 'to': u"orm['hosts.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
            'notification': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'hosts.notificationtohost': {
            'Meta': {'object_name': 'NotificationToHost', 'db_table': "'notifications_to_hosts'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
            'nid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Notification']", 'db_column': "'nid'"})
        },
        u'hosts.structuredattributetohost': {
            'Meta': {'object_name': 'StructuredAttributeToHost', 'db_table': "'structured_attributes_to_hosts'"},
            'avid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.StructuredAttributeValue']", 'db_column': "'avid'"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"})
        },
        u'hosts.structuredattributevalue': {
            'Meta': {'object_name': 'StructuredAttributeValue', 'db_table': "'structured_attribute_values'"},
            'aid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Attribute']", 'db_column': "'aid'"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'network.addresstype': {
            'Meta': {'object_name': 'AddressType', 'db_table': "'addresstypes'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']", 'null': 'True', 'blank': 'True'}),
            'ranges': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['network.NetworkRange']", 'null': 'True', 'blank': 'True'})
        },
        u'network.dhcpgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DhcpGroup', 'db_table': "'dhcp_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['network.DhcpOption']", 'through': u"orm['network.DhcpOptionToDhcpGroup']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'network.dhcpoption': {
            'Meta': {'object_name': 'DhcpOption', 'db_table': "'dhcp_options'"},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'}),
            'option': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'network.dhcpoptiontodhcpgroup': {
            'Meta': {'object_name': 'DhcpOptionToDhcpGroup', 'db_table': "'dhcp_options_to_dhcp_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'option_values'", 'null': 'True', 'db_column': "'gid'", 'to': u"orm['network.DhcpGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oid': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'group_values'", 'null': 'True', 'db_column': "'oid'", 'to': u"orm['network.DhcpOption']"}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'network.hosttopool': {
            'Meta': {'object_name': 'HostToPool', 'db_table': "'hosts_to_pools'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']"})
        },
        u'network.networkrange': {
            'Meta': {'object_name': 'NetworkRange', 'db_table': "'network_ranges'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'range': ('netfields.fields.CidrAddressField', [], {'unique': 'True', 'max_length': '43'})
        },
        u'network.pool': {
            'Meta': {'object_name': 'Pool', 'db_table': "'pools'"},
            'allow_unknown': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lease_time': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.AuthSource']", 'db_column': "'source'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['hosts']
