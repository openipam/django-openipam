# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from openipam.core.utils.django_fk_hack import get_sql

def hack_django_fk_constraints(apps, schema_editor):

    cursor = schema_editor.connection.cursor()

    #not managed# migrations.RunSQL(get_sql('hosts_to_groups', 'hosts', 'mac')),
    cursor.execute(get_sql('structured_attributes_to_hosts', 'hosts', 'mac'))
    cursor.execute(get_sql('freeform_attributes_to_hosts', 'hosts', 'mac'))
    cursor.execute(get_sql('hosts_to_pools', 'hosts', 'mac'))
    cursor.execute(get_sql('notifications_to_hosts', 'hosts', 'mac'))

class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0004_auto_20140811_1110'),
    ]

    operations = [
        migrations.RunPython(hack_django_fk_constraints)
    ]

