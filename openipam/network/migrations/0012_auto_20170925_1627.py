# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-25 22:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("network", "0011_auto_20170925_1625")]

    operations = [
        migrations.AlterModelTable(name="building", table="buildings"),
        migrations.AlterModelTable(name="buildingtovlan", table="buildings_to_vlans"),
    ]