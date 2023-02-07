# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DhcpDnsRecord",
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
                ("ttl", models.IntegerField(default=-1, null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "dhcp_dns_records"},
            bases=(models.Model,),
        )
    ]
