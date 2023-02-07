# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [("network", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="lease",
            name="host",
            field=models.ForeignKey(
                db_constraint=False,
                null=True,
                db_column="mac",
                to="hosts.Host",
                unique=True,
            ),
        )
    ]
