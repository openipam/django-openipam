# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import djorm_pgfulltext.fields


class Migration(migrations.Migration):

    dependencies = [("hosts", "0006_auto_20150218_1326")]

    operations = [
        migrations.AddField(
            model_name="host",
            name="search_index",
            field=djorm_pgfulltext.fields.VectorField(
                default=b"", serialize=False, null=True, editable=False, db_index=True
            ),
            preserve_default=True,
        )
    ]
