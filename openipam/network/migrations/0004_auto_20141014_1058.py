# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [("taggit", "0001_initial"), ("network", "0003_auto_20140814_1541")]

    operations = [
        migrations.CreateModel(
            name="TaggedNetworks",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("content_object", models.ForeignKey(to="network.Network")),
                (
                    "tag",
                    models.ForeignKey(
                        related_name="network_taggednetworks_items", to="taggit.Tag"
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        )
    ]
