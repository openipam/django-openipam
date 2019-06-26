# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from openipam.core.utils.django_fk_hack import get_sql


def hack_django_fk_constraints(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute(get_sql("addresses", "hosts", "mac"))


class Migration(migrations.Migration):

    dependencies = [("network", "0002_auto_20140811_1110")]

    operations = [migrations.RunPython(hack_django_fk_constraints)]
