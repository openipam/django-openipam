# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("hosts", "0002_auto_20140807_1624")]

    operations = [
        migrations.AlterField(
            model_name="disabled",
            name="host",
            field=models.ForeignKey(
                db_constraint=False,
                primary_key=True,
                db_column="mac",
                serialize=False,
                to="hosts.Host",
            ),
        )
    ]
