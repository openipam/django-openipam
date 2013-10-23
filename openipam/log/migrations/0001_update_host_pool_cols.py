# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Pool.assignable'
        db.add_column('poolslog', 'assignable',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Host.address_type'
        db.add_column('hostlog', 'address_type_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Deleting field 'Pool.assignable'
        db.delete_column('pools', 'assignable')

        # Deleting field 'Host.address_type'
        db.delete_column('hostlog', 'address_type_id')


    models = {
        u'log.addresslog': {
            'Meta': {'object_name': 'AddressLog', 'db_table': "'addresses_log'", 'managed': 'False'},
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'network': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pool': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reserved': ('django.db.models.fields.BooleanField', [], {}),
            'trigger_changed': ('django.db.models.fields.DateTimeField', [], {}),
            'trigger_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'trigger_mode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'trigger_tuple': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'trigger_user': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'log.domainlog': {
            'Meta': {'object_name': 'DomainLog', 'db_table': "'domains_log'", 'managed': 'False'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {}),
            'last_check': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'master': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notified_serial': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'trigger_changed': ('django.db.models.fields.DateTimeField', [], {}),
            'trigger_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'trigger_mode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'trigger_tuple': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'trigger_user': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        u'log.hostlog': {
            'Meta': {'object_name': 'HostLog', 'db_table': "'hosts_log'", 'managed': 'False'},
            'address_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mac': ('django.db.models.fields.TextField', [], {}),
            'trigger_changed': ('django.db.models.fields.DateTimeField', [], {}),
            'trigger_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'trigger_mode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'trigger_tuple': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'trigger_user': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'log.poolslog': {
            'Meta': {'object_name': 'PoolsLog', 'db_table': "'pools_log'", 'managed': 'False'},
            'allow_unknown': ('django.db.models.fields.BooleanField', [], {}),
            'assignable': ('django.db.models.fields.BooleanField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dhcp_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {}),
            'lease_time': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'trigger_changed': ('django.db.models.fields.DateTimeField', [], {}),
            'trigger_id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'trigger_mode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'trigger_tuple': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'trigger_user': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['log']
