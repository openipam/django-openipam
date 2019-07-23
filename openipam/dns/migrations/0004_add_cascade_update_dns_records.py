# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from openipam.core.utils.django_fk_hack import get_sql


def hack_django_fk_constraints(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute(get_sql("dns_records", "hosts", "mac"))


class Migration(migrations.Migration):

    dependencies = [("dns", "0003_populate_dns_types")]

    operations = [migrations.RunPython(hack_django_fk_constraints)]
