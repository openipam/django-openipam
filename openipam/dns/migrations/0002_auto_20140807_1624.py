# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dns', '0001_initial'),
        ('hosts', '0001_initial'),
        ('network', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dhcpdnsrecord',
            name='ip_content',
            field=models.ForeignKey(db_column=b'ip_content', blank=True, to='network.Address', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhcpdnsrecord',
            name='name',
            field=models.ForeignKey(db_column=b'name', to_field=b'hostname', to='hosts.Host', unique=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='DnsRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, error_messages={b'blank': b'Name fields for DNS records cannot be blank.'})),
                ('text_content', models.CharField(max_length=255, null=True, blank=True)),
                ('ttl', models.IntegerField(default=86400, null=True, blank=True)),
                ('priority', models.IntegerField(null=True, verbose_name=b'Priority', blank=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column=b'changed_by')),
                ('host', models.ForeignKey(db_column=b'mac', blank=True, to='hosts.Host', null=True)),
                ('ip_content', models.ForeignKey(db_column=b'ip_content', blank=True, to='network.Address', null=True, verbose_name=b'IP Content')),
            ],
            options={
                'ordering': (b'dns_type', b'name'),
                'db_table': b'dns_records',
                'verbose_name': b'DNS Record',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DnsType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=16, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('min_permissions', models.ForeignKey(to='user.Permission', db_column=b'min_permissions')),
            ],
            options={
                'ordering': (b'name',),
                'db_table': b'dns_types',
                'verbose_name': b'DNS Type',
                'permissions': ((b'add_records_to_dnstype', b'Can add records to'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dnsrecord',
            name='dns_type',
            field=models.ForeignKey(db_column=b'tid', verbose_name=b'Type', error_messages={b'blank': b'Type fields for DNS records cannot be blank.'}, to='dns.DnsType'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='DnsView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': b'dns_views',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dnsrecord',
            name='dns_view',
            field=models.ForeignKey(db_column=b'vid', blank=True, to='dns.DnsView', null=True, verbose_name=b'View'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('master', models.CharField(default=None, max_length=128, null=True, blank=True)),
                ('last_check', models.IntegerField(null=True, blank=True)),
                ('type', models.CharField(max_length=6)),
                ('notified_serial', models.IntegerField(null=True, blank=True)),
                ('account', models.CharField(default=None, max_length=40, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column=b'changed_by')),
            ],
            options={
                'db_table': b'domains',
                'permissions': ((b'is_owner_domain', b'Is owner'), (b'add_records_to_domain', b'Can add records to')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dnsrecord',
            name='domain',
            field=models.ForeignKey(db_column=b'did', verbose_name=b'Domain', to='dns.Domain'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dhcpdnsrecord',
            name='did',
            field=models.ForeignKey(to='dns.Domain', db_column=b'did'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Supermaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=25)),
                ('nameserver', models.CharField(max_length=255)),
                ('account', models.CharField(default=None, max_length=40, null=True, blank=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column=b'changed_by')),
            ],
            options={
                'db_table': b'supermasters',
            },
            bases=(models.Model,),
        ),
    ]
