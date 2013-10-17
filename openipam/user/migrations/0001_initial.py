# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('users', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auth_user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.AuthSource'], db_column='source')),
            ('min_permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Permission'], db_column='min_permissions')),
        ))
        db.send_create_signal(u'user', ['User'])

        # Adding model 'Permission'
        db.create_table('permissions', (
            ('id', self.gf('django.db.models.fields.TextField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'user', ['Permission'])

        # Adding model 'UserToGroup'
        db.create_table('users_to_groups', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_groups', db_column='uid', to=orm['user.User'])),
            ('gid', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group_users', db_column='gid', to=orm['user.Group'])),
            ('permissions', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_permissions', db_column='permissions', to=orm['user.Permission'])),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
            ('host_permissions', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_host_permissions', db_column='host_permissions', to=orm['user.Permission'])),
        ))
        db.send_create_signal(u'user', ['UserToGroup'])

        # Adding model 'Group'
        db.create_table('groups', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(unique=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')()),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'user', ['Group'])

        # Adding model 'DomainToGroup'
        db.create_table('domains_to_groups', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('did', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.Domain'], db_column='did')),
            ('gid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Group'], db_column='gid')),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'user', ['DomainToGroup'])

        # Adding model 'HostToGroup'
        db.create_table('hosts_to_groups', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('mac', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hosts.Host'], db_column='mac')),
            ('gid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Group'], db_column='gid')),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'user', ['HostToGroup'])

        # Adding model 'NetworkToGroup'
        db.create_table('networks_to_groups', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('nid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Network'], db_column='nid')),
            ('gid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Group'], db_column='gid')),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'user', ['NetworkToGroup'])

        # Adding model 'PoolToGroup'
        db.create_table('pools_to_groups', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['network.Pool'], db_column='pool')),
            ('gid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Group'], db_column='gid')),
        ))
        db.send_create_signal(u'user', ['PoolToGroup'])

        # Adding model 'InternalAuth'
        db.create_table('internal_auth', (
            ('id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='internal_user', primary_key=True, db_column='id', to=orm['user.User'])),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')()),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.User'], db_column='changed_by')),
        ))
        db.send_create_signal(u'user', ['InternalAuth'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('users')

        # Deleting model 'Permission'
        db.delete_table('permissions')

        # Deleting model 'UserToGroup'
        db.delete_table('users_to_groups')

        # Deleting model 'Group'
        db.delete_table('groups')

        # Deleting model 'DomainToGroup'
        db.delete_table('domains_to_groups')

        # Deleting model 'HostToGroup'
        db.delete_table('hosts_to_groups')

        # Deleting model 'NetworkToGroup'
        db.delete_table('networks_to_groups')

        # Deleting model 'PoolToGroup'
        db.delete_table('pools_to_groups')

        # Deleting model 'InternalAuth'
        db.delete_table('internal_auth')


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
            'auth_user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
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
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_permissions'", 'db_column': "'permissions'", 'to': u"orm['user.Permission']"}),
            'uid': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_groups'", 'db_column': "'uid'", 'to': u"orm['user.User']"})
        }
    }

    complete_apps = ['user']
