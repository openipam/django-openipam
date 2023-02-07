# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 22:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import netfields.fields


class Migration(migrations.Migration):
    dependencies = [("hosts", "0011_auto_20150309_1518")]

    operations = [
        migrations.RemoveField(model_name="notificationtohost", name="host"),
        migrations.RemoveField(model_name="notificationtohost", name="notification"),
        migrations.AlterModelOptions(
            name="expirationtype",
            options={
                "ordering": ("expiration",),
                "permissions": (("is_owner_expiration_type", "Is owner"),),
            },
        ),
        migrations.AlterModelOptions(
            name="host",
            options={
                "default_permissions": ("add", "change", "delete", "view"),
                "ordering": ("hostname",),
                "permissions": (("is_owner_host", "Is owner"),),
            },
        ),
        migrations.RemoveField(model_name="disabled", name="host"),
        migrations.RemoveField(model_name="notification", name="hosts"),
        migrations.AddField(
            model_name="disabled",
            name="mac",
            field=netfields.fields.MACAddressField(
                default="00:00:00:00:00:00", primary_key=True, serialize=False
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="gulrecentarpbyaddress",
            name="address",
            field=models.ForeignKey(
                db_column="address",
                db_constraint=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ip_history",
                to="network.Address",
            ),
        ),
        migrations.AlterField(
            model_name="gulrecentarpbyaddress",
            name="host",
            field=models.OneToOneField(
                db_column="mac",
                db_constraint=False,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="ip_history",
                serialize=False,
                to="hosts.Host",
            ),
        ),
        migrations.AlterField(
            model_name="gulrecentarpbymac",
            name="address",
            field=models.ForeignKey(
                db_column="address",
                db_constraint=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mac_history",
                to="network.Address",
            ),
        ),
        migrations.AlterField(
            model_name="gulrecentarpbymac",
            name="host",
            field=models.OneToOneField(
                db_column="mac",
                db_constraint=False,
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                related_name="mac_history",
                serialize=False,
                to="hosts.Host",
            ),
        ),
        migrations.AlterField(
            model_name="host",
            name="pools",
            field=models.ManyToManyField(
                related_name="pool_hosts",
                through="network.HostToPool",
                to="network.Pool",
            ),
        ),
        migrations.DeleteModel(name="NotificationToHost"),
    ]
