# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("hosts", "0003_auto_20140808_1619")]

    operations = [
        migrations.AlterField(
            model_name="gulrecentarpbyaddress",
            name="host",
            field=models.ForeignKey(
                db_constraint=False,
                primary_key=True,
                db_column="mac",
                serialize=False,
                to="hosts.Host",
            ),
        ),
        migrations.AlterField(
            model_name="gulrecentarpbymac",
            name="host",
            field=models.ForeignKey(
                db_constraint=False,
                primary_key=True,
                db_column="mac",
                serialize=False,
                to="hosts.Host",
            ),
        ),
    ]
