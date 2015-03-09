# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0010_auto_20150309_1117'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oui',
            old_name='mask',
            new_name='start',
        ),
        migrations.RenameField(
            model_name='oui',
            old_name='oui',
            new_name='stop',
        ),
        migrations.RunSQL(
            sql='CREATE INDEX ouis_range_index ON ouis(start, stop)',
            reverse_sql='DROP INDEX ouis_range_index'
        )
    ]
