# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import netfields.fields


class Migration(migrations.Migration):

    dependencies = [("hosts", "0005_hack_django_fk")]

    operations = [
        migrations.CreateModel(
            name="AttributeToHost",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "attribute",
                    models.IntegerField(null=True, db_column="aid", blank=True),
                ),
                ("name", models.CharField(max_length=255, null=True, blank=True)),
                ("structured", models.BooleanField(default=None)),
                ("required", models.BooleanField(default=False)),
                ("mac", netfields.fields.MACAddressField(null=True, blank=True)),
                ("avid", models.IntegerField(null=True, blank=True)),
                ("value", models.TextField(null=True, blank=True)),
            ],
            options={"db_table": "attributes_to_hosts", "managed": False},
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name="disabled",
            name="host",
            field=models.ForeignKey(
                related_name="disabled_host",
                primary_key=True,
                db_column="mac",
                db_constraint=False,
                serialize=False,
                to="hosts.Host",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="freeformattributetohost",
            name="host",
            field=models.ForeignKey(
                related_name="freeform_attributes", db_column="mac", to="hosts.Host"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="gulrecentarpbyaddress",
            name="host",
            field=models.ForeignKey(
                related_name="ip_history",
                primary_key=True,
                db_column="mac",
                db_constraint=False,
                serialize=False,
                to="hosts.Host",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="gulrecentarpbymac",
            name="host",
            field=models.ForeignKey(
                related_name="mac_history",
                primary_key=True,
                db_column="mac",
                db_constraint=False,
                serialize=False,
                to="hosts.Host",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="host",
            name="mac",
            field=netfields.fields.MACAddressField(
                serialize=False, verbose_name="Mac Address", primary_key=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="host",
            name="pools",
            field=models.ManyToManyField(
                related_name="pool_hosts",
                null=True,
                through="network.HostToPool",
                to="network.Pool",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="macoui",
            name="oui",
            field=netfields.fields.MACAddressField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="notification",
            name="hosts",
            field=models.ManyToManyField(
                related_name="host_notifications",
                through="hosts.NotificationToHost",
                to="hosts.Host",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="structuredattributetohost",
            name="host",
            field=models.ForeignKey(
                related_name="structured_attributes", db_column="mac", to="hosts.Host"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="structuredattributevalue",
            name="attribute",
            field=models.ForeignKey(
                related_name="choices", db_column="aid", to="hosts.Attribute"
            ),
            preserve_default=True,
        ),
    ]
