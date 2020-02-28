# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HostLog",
            fields=[
                ("trigger_mode", models.CharField(max_length=10)),
                ("trigger_tuple", models.CharField(max_length=5)),
                ("trigger_changed", models.DateTimeField()),
                (
                    "trigger_id",
                    models.BigIntegerField(serialize=False, primary_key=True),
                ),
                ("trigger_user", models.CharField(max_length=32)),
                ("mac", models.TextField()),
                ("hostname", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "address_type",
                    models.IntegerField(
                        null=True, db_column="address_type_id", blank=True
                    ),
                ),
                ("dhcp_group", models.IntegerField(null=True, blank=True)),
                ("expires", models.DateTimeField()),
                ("changed", models.DateTimeField(null=True, blank=True)),
            ],
            options={"db_table": "hosts_log", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PoolLog",
            fields=[
                ("trigger_mode", models.CharField(max_length=10)),
                ("trigger_tuple", models.CharField(max_length=5)),
                ("trigger_changed", models.DateTimeField()),
                (
                    "trigger_id",
                    models.BigIntegerField(serialize=False, primary_key=True),
                ),
                ("trigger_user", models.CharField(max_length=32)),
                ("id", models.IntegerField()),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("allow_unknown", models.BooleanField(default=False)),
                ("lease_time", models.IntegerField()),
                ("dhcp_group", models.IntegerField(null=True, blank=True)),
                ("assignable", models.BooleanField(default=False)),
            ],
            options={"db_table": "pools_log", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EmailLog",
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
                ("when", models.DateTimeField(auto_now_add=True)),
                ("to", models.EmailField(max_length=255)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
            ],
            options={"db_table": "email_log"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserLog",
            fields=[
                ("trigger_mode", models.CharField(max_length=10)),
                ("trigger_tuple", models.CharField(max_length=5)),
                ("trigger_changed", models.DateTimeField()),
                (
                    "trigger_id",
                    models.BigIntegerField(serialize=False, primary_key=True),
                ),
                ("trigger_user", models.CharField(max_length=32)),
                ("id", models.IntegerField()),
                ("username", models.CharField(max_length=50)),
                ("source", models.IntegerField()),
                ("min_permissions", models.CharField(max_length=8)),
                ("password", models.CharField(default="!", max_length=128)),
                ("last_login", models.DateTimeField(null=True, blank=True)),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_ipamadmin", models.BooleanField(default=False)),
                ("first_name", models.CharField(max_length=255, null=True, blank=True)),
                ("last_name", models.CharField(max_length=255, null=True, blank=True)),
                ("email", models.CharField(max_length=255, null=True, blank=True)),
                ("date_joined", models.DateTimeField(null=True, blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"db_table": "users_log", "managed": True},
            bases=(models.Model,),
        ),
    ]
