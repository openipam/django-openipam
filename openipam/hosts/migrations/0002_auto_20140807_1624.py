# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import netfields.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
        ("network", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hosts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="host",
            name="address_type_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                db_column=b"address_type_id",
                blank=True,
                to="network.AddressType",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="host",
            name="changed_by",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, db_column=b"changed_by"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="host",
            name="dhcp_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                db_column=b"dhcp_group",
                blank=True,
                to="network.DhcpGroup",
                null=True,
                verbose_name=b"DHCP Group",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="host",
            name="pools",
            field=models.ManyToManyField(
                to="network.Pool", null=True, through="network.HostToPool", blank=True
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="MacOui",
            fields=[
                (
                    "oui",
                    netfields.fields.MACAddressField(
                        max_length=17, serialize=False, primary_key=True
                    ),
                ),
                ("vendor", models.TextField()),
            ],
            options={"db_table": b"mac_oui"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("notification", models.DateField()),
                (
                    "min_permissions",
                    models.ForeignKey(
                        to="user.Permission", db_column=b"min_permissions"
                    ),
                ),
            ],
            options={"db_table": b"notifications"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotificationToHost",
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
                ("host", models.ForeignKey(to="hosts.Host", db_column=b"mac")),
            ],
            options={"db_table": b"notifications_to_hosts"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="notification",
            name="hosts",
            field=models.ManyToManyField(
                to="hosts.Host", through="hosts.NotificationToHost"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="notificationtohost",
            name="notification",
            field=models.ForeignKey(to="hosts.Notification", db_column=b"nid"),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="StructuredAttributeToHost",
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
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column=b"changed_by"
                    ),
                ),
                ("host", models.ForeignKey(to="hosts.Host", db_column=b"mac")),
            ],
            options={"db_table": b"structured_attributes_to_hosts"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StructuredAttributeValue",
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
                ("value", models.TextField()),
                ("is_default", models.BooleanField(default=False)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "attribute",
                    models.ForeignKey(to="hosts.Attribute", db_column=b"aid"),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column=b"changed_by"
                    ),
                ),
            ],
            options={
                "ordering": (b"attribute__name", b"value"),
                "db_table": b"structured_attribute_values",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="structuredattributetohost",
            name="structured_attribute_value",
            field=models.ForeignKey(
                to="hosts.StructuredAttributeValue", db_column=b"avid"
            ),
            preserve_default=True,
        ),
    ]
