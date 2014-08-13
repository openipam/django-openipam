# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from openipam.core.utils.django_fk_hack import get_sql

class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0003_auto_20140808_1619'),
    ]

    operations = [
                  migrations.RunSQL(get_sql('structured_attributes_to_hosts', 'hosts', 'mac')),
                  migrations.RunSQL(get_sql('freeform_attributes_to_hosts', 'hosts', 'mac')),
                  #not managed# migrations.RunSQL(get_sql('hosts_to_groups', 'hosts', 'mac')),
                  migrations.RunSQL(get_sql('hosts_to_pools', 'hosts', 'mac')),
                  migrations.RunSQL(get_sql('notifications_to_hosts', 'hosts', 'mac')),
                 ]

