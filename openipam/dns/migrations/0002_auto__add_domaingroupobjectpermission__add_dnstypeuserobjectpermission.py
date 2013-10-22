# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from bitstring import Bits


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DomainGroupObjectPermission'
        db.create_table(u'dns_domaingroupobjectpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_permissions', to=orm['dns.Domain'])),
        ))
        db.send_create_signal(u'dns', ['DomainGroupObjectPermission'])

        # Adding model 'DnsTypeUserObjectPermission'
        db.create_table(u'dns_dnstypeuserobjectpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_permissions', to=orm['dns.DnsType'])),
        ))
        db.send_create_signal(u'dns', ['DnsTypeUserObjectPermission'])

        # Adding unique constraint on 'DnsTypeUserObjectPermission', fields ['user', 'permission', 'content_object']
        db.create_unique(u'dns_dnstypeuserobjectpermission', ['user_id', 'permission_id', 'content_object_id'])

        # Adding model 'DomainUserObjectPermission'
        db.create_table(u'dns_domainuserobjectpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_permissions', to=orm['dns.Domain'])),
        ))
        db.send_create_signal(u'dns', ['DomainUserObjectPermission'])

        # Adding model 'DnsTypeGroupObjectPermission'
        db.create_table(u'dns_dnstypegroupobjectpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('content_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_permissions', to=orm['dns.DnsType'])),
        ))
        db.send_create_signal(u'dns', ['DnsTypeGroupObjectPermission'])

        # Adding unique constraint on 'DnsTypeGroupObjectPermission', fields ['group', 'permission', 'content_object']
        db.create_unique(u'dns_dnstypegroupobjectpermission', ['group_id', 'permission_id', 'content_object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DnsTypeGroupObjectPermission', fields ['group', 'permission', 'content_object']
        db.delete_unique(u'dns_dnstypegroupobjectpermission', ['group_id', 'permission_id', 'content_object_id'])

        # Removing unique constraint on 'DnsTypeUserObjectPermission', fields ['user', 'permission', 'content_object']
        db.delete_unique(u'dns_dnstypeuserobjectpermission', ['user_id', 'permission_id', 'content_object_id'])

        # Deleting model 'DomainGroupObjectPermission'
        db.delete_table(u'dns_domaingroupobjectpermission')

        # Deleting model 'DnsTypeUserObjectPermission'
        db.delete_table(u'dns_dnstypeuserobjectpermission')

        # Deleting model 'DomainUserObjectPermission'
        db.delete_table(u'dns_domainuserobjectpermission')

        # Deleting model 'DnsTypeGroupObjectPermission'
        db.delete_table(u'dns_dnstypegroupobjectpermission')


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
        u'dns.dhcpdnsrecord': {
            'Meta': {'object_name': 'DhcpDnsRecord', 'db_table': "'dhcp_dns_records'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'did': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']", 'db_column': "'did'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_content': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Address']", 'null': 'True', 'db_column': "'ip_content'", 'blank': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hosts.Host']", 'unique': 'True', 'db_column': "'name'"}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'null': 'True', 'blank': 'True'})
        },
        u'dns.dnsrecord': {
            'Meta': {'ordering': "('dns_type', 'name')", 'object_name': 'DnsRecord', 'db_table': "'dns_records'"},
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'dns_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.DnsType']", 'db_column': "'tid'"}),
            'dns_view': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.DnsView']", 'null': 'True', 'db_column': "'vid'", 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']", 'db_column': "'did'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_content': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['network.Address']", 'null': 'True', 'db_column': "'ip_content'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text_content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '86400', 'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('name',)", 'object_name': 'DnsType', 'db_table': "'dns_types'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.Permission']", 'db_column': "'min_permissions'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        },
        u'dns.dnstypegroupobjectpermission': {
            'Meta': {'unique_together': "([u'group', u'permission', u'content_object'],)", 'object_name': 'DnsTypeGroupObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_permissions'", 'to': u"orm['dns.DnsType']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"})
        },
        u'dns.dnstypeuserobjectpermission': {
            'Meta': {'unique_together': "([u'user', u'permission', u'content_object'],)", 'object_name': 'DnsTypeUserObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_permissions'", 'to': u"orm['dns.DnsType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"})
        },
        u'dns.dnsview': {
            'Meta': {'object_name': 'DnsView', 'db_table': "'dns_views'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'dns.domain': {
            'Meta': {'object_name': 'Domain', 'db_table': "'domains'"},
            'account': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        u'dns.domaingroupobjectpermission': {
            'Meta': {'object_name': 'DomainGroupObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_permissions'", 'to': u"orm['dns.Domain']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"})
        },
        u'dns.domainuserobjectpermission': {
            'Meta': {'object_name': 'DomainUserObjectPermission'},
            'content_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_permissions'", 'to': u"orm['dns.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']"})
        },
        u'dns.pdnszonexfer': {
            'Meta': {'object_name': 'PdnsZoneXfer', 'db_table': "'pdns_zone_xfer'", 'managed': 'False'},
            'change_date': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dns.Domain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'prio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'view_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'dns.supermaster': {
            'Meta': {'object_name': 'Supermaster', 'db_table': "'supermasters'"},
            'account': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user.User']", 'db_column': "'changed_by'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'nameserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'changed': ('django.db.models.fields.DateTimeField', [], {}),
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
        u'network.dhcpgroup': {
            'Meta': {'object_name': 'DhcpGroup', 'db_table': "'dhcp_groups'"},
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
        u'network.networkrange': {
            'Meta': {'object_name': 'NetworkRange', 'db_table': "'network_ranges'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'range': ('netfields.fields.CidrAddressField', [], {'unique': 'True', 'max_length': '43'})
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

    complete_apps = ['dns']
