# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import os


def get_initial_sql_list(filename):
    sqlCommands = list()
    sqlFile = open(filename, 'r')
    line = sqlFile.readline()
    sqlCommand = sqlFile.read()

    return sqlCommand

class Migration(migrations.Migration):

    operations = [
        migrations.RunSQL(get_initial_sql_list('sql/openipam-initial.sql')),
    ]
