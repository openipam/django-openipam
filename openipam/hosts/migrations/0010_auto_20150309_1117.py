# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0009_auto_20150306_1720'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='oui',
            table='ouis',
        ),
    ]
