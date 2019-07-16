# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
import taggit.managers
import djorm_pgfulltext.fields


class Migration(migrations.Migration):

    dependencies = [("taggit", "0001_initial"), ("network", "0004_auto_20141014_1058")]

    operations = [
        migrations.AddField(
            model_name="network",
            name="search_index",
            field=djorm_pgfulltext.fields.VectorField(
                default="", serialize=False, null=True, editable=False, db_index=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="network",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="network.TaggedNetworks",
                blank=True,
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="address",
            name="host",
            field=models.ForeignKey(
                related_name="addresses",
                on_delete=django.db.models.deletion.SET_NULL,
                db_column="mac",
                blank=True,
                to="hosts.Host",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="address",
            name="network",
            field=models.ForeignKey(
                related_name="net_addresses", db_column="network", to="network.Network"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="addresstype",
            name="ranges",
            field=models.ManyToManyField(
                related_name="address_ranges",
                null=True,
                to="network.NetworkRange",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="defaultpool",
            name="pool",
            field=models.ForeignKey(
                related_name="pool_defaults", blank=True, to="network.Pool", null=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="dhcpoptiontodhcpgroup",
            name="group",
            field=models.ForeignKey(
                related_name="option_values",
                db_column="gid",
                blank=True,
                to="network.DhcpGroup",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="dhcpoptiontodhcpgroup",
            name="option",
            field=models.ForeignKey(
                related_name="group_values",
                db_column="oid",
                blank=True,
                to="network.DhcpOption",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="hosttopool",
            name="host",
            field=models.ForeignKey(
                related_name="host_pools", db_column="mac", to="hosts.Host"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="hosttopool",
            name="pool",
            field=models.ForeignKey(related_name="host_pools", to="network.Pool"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="lease",
            name="address",
            field=models.ForeignKey(
                related_name="leases",
                primary_key=True,
                db_column="address",
                serialize=False,
                to="network.Address",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="lease",
            name="host",
            field=models.ForeignKey(
                related_name="leases",
                null=True,
                db_column="mac",
                db_constraint=False,
                to="hosts.Host",
                unique=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="network",
            name="vlans",
            field=models.ManyToManyField(
                related_name="vlan_networks",
                through="network.NetworkToVlan",
                to="network.Vlan",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="vlan",
            name="name",
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
