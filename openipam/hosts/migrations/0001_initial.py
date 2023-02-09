# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import netfields.fields
import openipam.hosts.validators
from django.conf import settings
import openipam.core.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attribute",
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
                ("name", models.CharField(unique=True, max_length=255)),
                ("description", models.TextField(null=True, blank=True)),
                ("structured", models.BooleanField(default=False)),
                ("required", models.BooleanField(default=False)),
                ("validation", models.TextField(null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "attributes"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Disabled",
            fields=[
                (
                    "host",
                    netfields.fields.MACAddressField(
                        max_length=17,
                        serialize=False,
                        primary_key=True,
                        db_column="mac",
                    ),
                ),
                ("reason", models.TextField(null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True, db_column="disabled")),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="disabled_by"
                    ),
                ),
            ],
            options={
                "ordering": ("-changed",),
                "db_table": "disabled",
                "verbose_name": "Disabled Host",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ExpirationType",
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
                ("expiration", models.DateTimeField()),
                (
                    "min_permissions",
                    models.ForeignKey(
                        to="user.Permission", db_column="min_permissions"
                    ),
                ),
            ],
            options={"ordering": ("expiration",), "db_table": "expiration_types"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FreeformAttributeToHost",
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
                ("changed", models.DateTimeField(auto_now=True)),
                ("attribute", models.ForeignKey(to="hosts.Attribute", db_column="aid")),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "freeform_attributes_to_hosts"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GuestTicket",
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
                ("ticket", models.CharField(unique=True, max_length=255)),
                ("starts", models.DateTimeField()),
                ("ends", models.DateTimeField()),
                ("description", models.TextField(null=True, blank=True)),
                (
                    "user",
                    models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column="uid"),
                ),
            ],
            options={"db_table": "guest_tickets"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "mac",
                    netfields.fields.MACAddressField(
                        max_length=17,
                        serialize=False,
                        verbose_name="Mac Address",
                        primary_key=True,
                    ),
                ),
                (
                    "hostname",
                    models.CharField(
                        db_index=True,
                        unique=True,
                        max_length=255,
                        validators=[openipam.hosts.validators.validate_hostname],
                    ),
                ),
                ("description", models.TextField(null=True, blank=True)),
                ("expires", models.DateTimeField()),
                ("changed", models.DateTimeField(auto_now=True)),
                ("last_notified", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "ordering": ("hostname",),
                "db_table": "hosts",
                "permissions": (("is_owner_host", "Is owner"),),
            },
            bases=(openipam.core.mixins.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="GulRecentArpBymac",
            fields=[
                (
                    "host",
                    models.ForeignKey(
                        primary_key=True,
                        db_column="mac",
                        serialize=False,
                        to="hosts.Host",
                    ),
                ),
                ("address", netfields.fields.InetAddressField(max_length=39)),
                ("stopstamp", models.DateTimeField()),
            ],
            options={"db_table": "gul_recent_arp_bymac"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GulRecentArpByaddress",
            fields=[
                (
                    "host",
                    models.ForeignKey(
                        primary_key=True,
                        db_column="mac",
                        serialize=False,
                        to="hosts.Host",
                    ),
                ),
                ("address", netfields.fields.InetAddressField(max_length=39)),
                ("stopstamp", models.DateTimeField()),
            ],
            options={"db_table": "gul_recent_arp_byaddress"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="freeformattributetohost",
            name="host",
            field=models.ForeignKey(to="hosts.Host", db_column="mac"),
            preserve_default=True,
        ),
    ]
