# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [("user", "0002_populate_permissions")]

    operations = [
        migrations.CreateModel(
            name="DomainToGroup",
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
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "domains_to_groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Group",
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
                ("name", models.TextField(unique=True, blank=True)),
                ("description", models.TextField(blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HostToGroup",
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
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "hosts_to_groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="InternalAuth",
            fields=[
                (
                    "id",
                    models.ForeignKey(
                        related_name="internal_user",
                        primary_key=True,
                        db_column="id",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("password", models.CharField(max_length=128, db_column="hash")),
                ("name", models.CharField(max_length=255, blank=True)),
                ("email", models.CharField(max_length=255, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "internal_auth", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NetworkToGroup",
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
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "networks_to_groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PoolToGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                )
            ],
            options={"db_table": "pools_to_groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UserToGroup",
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
                ("changed", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "users_to_groups", "managed": False},
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name="groupsource",
            name="group",
            field=models.OneToOneField(
                related_name="source",
                primary_key=True,
                serialize=False,
                to="auth.Group",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="groupsource",
            name="source",
            field=models.ForeignKey(
                related_name="group",
                db_column="source",
                default=1,
                to="user.AuthSource",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                related_query_name="user",
                related_name="user_set",
                to="auth.Group",
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                verbose_name="groups",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="user",
            name="min_permissions",
            field=models.ForeignKey(
                related_name="user_min_permissions",
                db_column="min_permissions",
                blank=True,
                to="user.Permission",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="user",
            name="source",
            field=models.ForeignKey(
                db_column="source", blank=True, to="user.AuthSource", null=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                related_query_name="user",
                related_name="user_set",
                to="auth.Permission",
                blank=True,
                help_text="Specific permissions for this user.",
                verbose_name="user permissions",
            ),
            preserve_default=True,
        ),
    ]
