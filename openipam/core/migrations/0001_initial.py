# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import guardian.migrations

import os


class Migration(migrations.Migration):

    initial = True


def get_initial_sql_list(filename):
    sqlCommands = list()
    sqlFile = open(filename, 'r')
    line = sqlFile.readline()
    sqlCommand = sqlFile.read()

    return sqlCommand

class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('dns', '0002_auto_20161201_1426'),
        ('hosts', '0002_auto_20161201_1426'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL("ALTER TABLE users ALTER COLUMN min_permissions TYPE BIT USING(min_permissions::bit);"),
        migrations.RunSQL(get_initial_sql_list('sql/openipam-initial.sql')),
        migrations.RunSQL("INSERT INTO auth_sources (id, name) VALUES (1, 'anonymous_source');"),
        migrations.RunSQL("INSERT INTO permissions (id, name, description) VALUES \
                            (b'00000000', 'anonymous', 'Permissions for Anonymous user');"),
    ]
