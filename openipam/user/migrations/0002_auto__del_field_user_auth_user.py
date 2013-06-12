# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'User.auth_user'
        db.delete_column('users', 'auth_user_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'User.auth_user'
        raise RuntimeError("Cannot reverse this migration. 'User.auth_user' and its values cannot be restored.")

    models = {
        u'dns.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "'domains'"},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
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
        u'hosts.freeformattributetohost': {
            'Meta': {'object_name': 'FreeformAttributeToHost', 'db_table': "'freeform_attributes_to_hosts'"},
            'aid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Attribute']", 'db_column': "'aid'"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'hosts.host': {
            'Meta': {'object_name': 'Host', 'db_table': "'hosts'"},
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
        u'network.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'networks'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.DhcpGroup']", 'null': 'True', 'db_column': "'dhcp_group'", 'blank': 'True'}),
            'gateway': ('netfields.fields.InetAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'network': ('netfields.fields.CidrAddressField', [], {'max_length': '43', 'primary_key': 'True'}),
            'shared_network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.SharedNetwork']", 'null': 'True', 'db_column': "'shared_network'", 'blank': 'True'}),
            'vlans': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'vlan_networks'", 'symmetrical': 'False', 'through': u"orm['network.NetworkToVlan']", 'to': u"orm['network.Vlan']"})
        },
        u'network.networktovlan': {
            'Meta': {'object_name': 'NetworkToVlan', 'db_table': "'networks_to_vlans'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Network']", 'primary_key': 'True', 'db_column': "'network'"}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Vlan']", 'db_column': "'vlan'"})
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
        u'network.sharednetwork': {
            'Meta': {'object_name': 'SharedNetwork', 'db_table': "'shared_networks'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
        u'user.authsource': {
            'Meta': {'object_name': 'AuthSource', 'db_table': "'auth_sources'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'})
        },
        u'user.domaintogroup': {
            'Meta': {'object_name': 'DomainToGroup', 'db_table': "'domains_to_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'did': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']", 'db_column': "'did'"}),
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Group']", 'db_column': "'gid'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'user.group': {
            'Meta': {'object_name': 'Group', 'db_table': "'groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'})
        },
        u'user.hosttogroup': {
            'Meta': {'object_name': 'HostToGroup', 'db_table': "'hosts_to_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Group']", 'db_column': "'gid'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'db_column': "'mac'"})
        },
        u'user.internalauth': {
            'Meta': {'object_name': 'InternalAuth', 'db_table': "'internal_auth'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'internal_user'", 'primary_key': 'True', 'db_column': "'id'", 'to': u"orm['user.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'user.networktogroup': {
            'Meta': {'object_name': 'NetworkToGroup', 'db_table': "'networks_to_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Group']", 'db_column': "'gid'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Network']", 'db_column': "'nid'"})
        },
        u'user.permission': {
            'Meta': {'object_name': 'Permission', 'db_table': "'permissions'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.TextField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'user.pooltogroup': {
            'Meta': {'object_name': 'PoolToGroup', 'db_table': "'pools_to_groups'"},
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Group']", 'db_column': "'gid'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Pool']", 'db_column': "'pool'"})
        },
        u'user.user': {
            'Meta': {'object_name': 'User', 'db_table': "'users'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.AuthSource']", 'db_column': "'source'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'user.usertogroup': {
            'Meta': {'object_name': 'UserToGroup', 'db_table': "'users_to_groups'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'gid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_users'", 'db_column': "'gid'", 'to': u"orm['user.Group']"}),
            'host_permissions': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_host_permissions'", 'db_column': "'host_permissions'", 'to': u"orm['user.Permission']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_permissions'", 'db_column': "'permissions'", 'to': u"orm['user.Permission']"}),
            'uid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_groups'", 'db_column': "'uid'", 'to': u"orm['user.User']"})
        }
    }

    complete_apps = ['user']