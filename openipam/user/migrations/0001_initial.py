# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("auth", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("username", models.CharField(unique=True, max_length=50)),
                (
                    "first_name",
                    models.CharField(
                        max_length=255, verbose_name="first name", blank=True
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=255, verbose_name="last name", blank=True
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=255, verbose_name="email address", blank=True
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        to="auth.Group", verbose_name="groups", blank=True
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        to="auth.Permission",
                        verbose_name="user permissions",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": b"users",
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AuthSource",
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
                ("name", models.CharField(unique=True, max_length=255, blank=True)),
            ],
            options={"db_table": b"auth_sources"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="user",
            name="source",
            field=models.ForeignKey(
                db_column=b"source",
                default=None,
                blank=True,
                to="user.AuthSource",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="GroupSource",
            fields=[
                (
                    "group",
                    models.OneToOneField(
                        primary_key=True, serialize=False, to="auth.Group"
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        db_column=b"source", default=1, to="user.AuthSource"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Permission",
            fields=[
                (
                    "permission",
                    models.CharField(
                        max_length=8, serialize=False, primary_key=True, db_column=b"id"
                    ),
                ),
                ("name", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"db_table": b"permissions"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="user",
            name="min_permissions",
            field=models.ForeignKey(
                db_column=b"min_permissions",
                default=None,
                blank=True,
                to="user.Permission",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
