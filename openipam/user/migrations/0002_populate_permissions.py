# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_none_permission(apps, schema_editor):
    Permission = apps.get_model('user', 'Permission')

    Permission.objects.get_or_create(
        permission='00000000',
        name='NONE',
        description='No permissions'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_none_permission)
    ]
