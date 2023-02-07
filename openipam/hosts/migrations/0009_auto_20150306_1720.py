# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [("hosts", "0008_oui")]

    operations = [
        migrations.AlterField(
            model_name="oui",
            name="shortname",
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        )
    ]
