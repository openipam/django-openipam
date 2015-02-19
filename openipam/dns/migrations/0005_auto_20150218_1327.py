# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dns', '0004_add_cascade_update_dns_records'),
    ]

    operations = [
        migrations.CreateModel(
            name='DnsRecordMunged',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('type', models.CharField(max_length=32, blank=True)),
                ('content', models.TextField(blank=True)),
                ('ttl', models.IntegerField(null=True, blank=True)),
                ('prio', models.IntegerField(null=True, blank=True)),
                ('change_date', models.IntegerField(null=True, blank=True)),
                ('view_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'dns_records_munged',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PdnsZoneXfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=10)),
                ('content', models.CharField(max_length=255)),
                ('ttl', models.IntegerField(null=True, blank=True)),
                ('priority', models.IntegerField(null=True, blank=True)),
                ('change_date', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'pdns_zone_xfer',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('type', models.CharField(max_length=32, blank=True)),
                ('content', models.TextField(blank=True)),
                ('ttl', models.IntegerField(null=True, blank=True)),
                ('prio', models.IntegerField(null=True, blank=True)),
                ('change_date', models.IntegerField(null=True, blank=True)),
                ('view_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'records',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordMunged',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('type', models.CharField(max_length=255, blank=True)),
                ('content', models.TextField(blank=True)),
                ('ttl', models.IntegerField(null=True, blank=True)),
                ('prio', models.IntegerField(null=True, blank=True)),
                ('change_date', models.IntegerField(null=True, blank=True)),
                ('view_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'records_munged',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='dnsrecord',
            name='dns_type',
            field=models.ForeignKey(related_name='records', db_column=b'tid', verbose_name=b'Type', error_messages={b'blank': b'Type fields for DNS records cannot be blank.'}, to='dns.DnsType'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dnsrecord',
            name='host',
            field=models.ForeignKey(related_name='dns_records', db_column=b'mac', blank=True, to='hosts.Host', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dnsrecord',
            name='ip_content',
            field=models.ForeignKey(related_name='arecords', db_column=b'ip_content', blank=True, to='network.Address', null=True, verbose_name=b'IP Content'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dnsrecord',
            name='ttl',
            field=models.IntegerField(default=14400, null=True, blank=True),
            preserve_default=True,
        ),
    ]
