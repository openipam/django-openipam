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
        ('core', '0002_featurerequest_user'),
        ('network', '0002_auto_20161202_1415'),
        ('dns', '0002_auto_20161202_1415'),
        ('hosts', '0002_auto_20161202_1415'),
        ('log', '0001_initial'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        #migrations.RunSQL(get_initial_sql_list('sql/openipam-initial.sql')),
        #migrations.RunSQL(get_initial_sql_list('sql/apgdiff.sql')),
        migrations.RunSQL("INSERT INTO auth_sources (id, name) VALUES (1, 'anonymous_source');"),
        migrations.RunSQL("INSERT INTO permissions (id, name, description) VALUES \
                            (b'00000000', 'anonymous', 'Permissions for Anonymous user');"),
    ]

