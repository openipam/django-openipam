# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import netfields.fields


class Migration(migrations.Migration):
    dependencies = [("hosts", "0007_host_search_index")]

    operations = [
        migrations.CreateModel(
            name="OUI",
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
                ("oui", netfields.fields.MACAddressField()),
                ("mask", netfields.fields.MACAddressField()),
                ("shortname", models.CharField(max_length=32, null=True, blank=True)),
                ("name", models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        )
    ]
