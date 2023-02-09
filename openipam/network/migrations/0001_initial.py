# -*- coding: utf-8 -*-


from django.db import models, migrations
import netfields.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("hosts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "address",
                    netfields.fields.InetAddressField(
                        max_length=39, serialize=False, primary_key=True
                    ),
                ),
                ("reserved", models.BooleanField(default=False)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
                (
                    "host",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        db_column="mac",
                        blank=True,
                        to="hosts.Host",
                        null=True,
                    ),
                ),
            ],
            options={"db_table": "addresses", "verbose_name_plural": "addresses"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AddressType",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={"ordering": ("name",), "db_table": "addresstypes"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DefaultPool",
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
                ("cidr", netfields.fields.CidrAddressField(unique=True, max_length=43)),
            ],
            options={"db_table": "default_pools"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DhcpGroup",
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
                ("name", models.SlugField()),
                ("description", models.TextField(null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "dhcp_groups", "verbose_name": "DHCP group"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DhcpOption",
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
                ("size", models.CharField(max_length=10, null=True, blank=True)),
                (
                    "name",
                    models.CharField(
                        max_length=255, unique=True, null=True, blank=True
                    ),
                ),
                (
                    "option",
                    models.CharField(
                        max_length=255, unique=True, null=True, blank=True
                    ),
                ),
                ("comment", models.TextField(null=True, blank=True)),
            ],
            options={"db_table": "dhcp_options", "verbose_name": "DHCP option"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DhcpOptionToDhcpGroup",
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
                ("value", models.BinaryField(null=True, editable=False, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "dhcp_options_to_dhcp_groups"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="dhcpgroup",
            name="dhcp_options",
            field=models.ManyToManyField(
                to="network.DhcpOption", through="network.DhcpOptionToDhcpGroup"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dhcpoptiontodhcpgroup",
            name="group",
            field=models.ForeignKey(
                db_column="gid", blank=True, to="network.DhcpGroup", null=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dhcpoptiontodhcpgroup",
            name="option",
            field=models.ForeignKey(
                db_column="oid", blank=True, to="network.DhcpOption", null=True
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="HostToPool",
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
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
                ("host", models.ForeignKey(to="hosts.Host", db_column="mac")),
            ],
            options={"db_table": "hosts_to_pools"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Lease",
            fields=[
                (
                    "address",
                    models.ForeignKey(
                        primary_key=True,
                        db_column="address",
                        serialize=False,
                        to="network.Address",
                    ),
                ),
                ("abandoned", models.BooleanField(default=False)),
                ("server", models.CharField(max_length=255, null=True, blank=True)),
                ("starts", models.DateTimeField()),
                ("ends", models.DateTimeField()),
                (
                    "host",
                    models.ForeignKey(
                        null=True, db_column="mac", to="hosts.Host", unique=True
                    ),
                ),
            ],
            options={"db_table": "leases"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Network",
            fields=[
                (
                    "network",
                    netfields.fields.CidrAddressField(
                        max_length=43, serialize=False, primary_key=True
                    ),
                ),
                ("name", models.CharField(max_length=255, null=True, blank=True)),
                (
                    "gateway",
                    netfields.fields.InetAddressField(
                        max_length=39, null=True, blank=True
                    ),
                ),
                ("description", models.TextField(null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
                (
                    "dhcp_group",
                    models.ForeignKey(
                        db_column="dhcp_group",
                        blank=True,
                        to="network.DhcpGroup",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("network",),
                "db_table": "networks",
                "permissions": (
                    ("is_owner_network", "Is owner"),
                    ("add_records_to_network", "Can add records to"),
                ),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="address",
            name="network",
            field=models.ForeignKey(to="network.Network", db_column="network"),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="NetworkRange",
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
                (
                    "range",
                    netfields.fields.CidrAddressField(unique=True, max_length=43),
                ),
            ],
            options={"db_table": "network_ranges"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="addresstype",
            name="ranges",
            field=models.ManyToManyField(
                to="network.NetworkRange", null=True, blank=True
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="NetworkToVlan",
            fields=[
                (
                    "network",
                    models.ForeignKey(
                        primary_key=True,
                        db_column="network",
                        serialize=False,
                        to="network.Network",
                    ),
                ),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "networks_to_vlans"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Pool",
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
                ("name", models.SlugField()),
                ("description", models.TextField(blank=True)),
                ("allow_unknown", models.BooleanField(default=False)),
                ("lease_time", models.IntegerField()),
                ("assignable", models.BooleanField(default=False)),
                (
                    "dhcp_group",
                    models.ForeignKey(
                        db_column="dhcp_group",
                        blank=True,
                        to="network.DhcpGroup",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "pools",
                "permissions": (("add_records_to_pool", "Can add records to"),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="hosttopool",
            name="pool",
            field=models.ForeignKey(to="network.Pool"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="defaultpool",
            name="pool",
            field=models.ForeignKey(blank=True, to="network.Pool", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="addresstype",
            name="pool",
            field=models.ForeignKey(blank=True, to="network.Pool", null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="address",
            name="pool",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                db_column="pool",
                blank=True,
                to="network.Pool",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="SharedNetwork",
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
                ("name", models.CharField(unique=True, max_length=255)),
                ("description", models.TextField(null=True, blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "shared_networks"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="network",
            name="shared_network",
            field=models.ForeignKey(
                db_column="shared_network",
                blank=True,
                to="network.SharedNetwork",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name="Vlan",
            fields=[
                ("id", models.SmallIntegerField(serialize=False, primary_key=True)),
                ("name", models.CharField(max_length=12)),
                ("description", models.TextField(blank=True)),
                ("changed", models.DateTimeField(null=True, blank=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, db_column="changed_by"
                    ),
                ),
            ],
            options={"db_table": "vlans"},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="networktovlan",
            name="vlan",
            field=models.ForeignKey(to="network.Vlan", db_column="vlan"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="network",
            name="vlans",
            field=models.ManyToManyField(
                to="network.Vlan", through="network.NetworkToVlan"
            ),
            preserve_default=True,
        ),
    ]
