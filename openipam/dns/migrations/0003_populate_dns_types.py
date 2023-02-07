# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

import json

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def populate_none_permission(apps, schema_editor):
    with open("{}/fixtures/dns_types.json".format(BASE_DIR)) as j:
        dns_types = json.loads(j.read())
    j.close()

    DnsType = apps.get_model("dns", "DnsType")
    Permission = apps.get_model("user", "Permission")

    for dns_type in dns_types:
        DnsType.objects.get_or_create(
            id=dns_type["pk"],
            name=dns_type["fields"]["name"],
            description=dns_type["fields"]["description"],
            min_permissions=Permission.objects.get(
                permission=dns_type["fields"]["min_permissions"]
            ),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("dns", "0002_auto_20140807_1624"),
        ("user", "0002_populate_permissions"),
    ]

    operations = [migrations.RunPython(populate_none_permission)]
