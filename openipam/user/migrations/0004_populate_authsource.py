# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_none_permission(apps, schema_editor):
    AuthSource = apps.get_model("user", "AuthSource")

    AuthSource.objects.get_or_create(name="INTERNAL")

    AuthSource.objects.get_or_create(name="LDAP")


class Migration(migrations.Migration):

    dependencies = [("user", "0003_auto_20150218_1327")]

    operations = [migrations.RunPython(populate_none_permission)]
