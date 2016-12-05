from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def get_initial_sql_list(filename):
    sqlCommands = list()
    sqlFile = open(filename, 'r')
    line = sqlFile.readline()
    sqlCommand = sqlFile.read()

    return sqlCommand


class Migration(migrations.Migration):


    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_foreign_key_constraints'),
        ('dashboard', '0001_initial'),
        ('django_cas_ng', '0001_initial'),
        ('menu', '0001_initial'),
        ('guardian', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(get_initial_sql_list('sql/modified-diff.sql')),
    ]

