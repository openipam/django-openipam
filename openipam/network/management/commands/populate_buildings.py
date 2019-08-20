from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from openipam.network.models import Building, BuildingToVlan, Vlan
from openipam.report.models import database

import json


User = get_user_model()


class Command(BaseCommand):
    args = ""
    help = "Populate building vlan data."

    def add_arguments(self, parser):

        parser.add_argument(
            "file", nargs="+", type=str, help="Specify json file to pull buildings."
        )

        # parser.add_argument('-t', '--test',
        #                     action='store_true',
        #                     dest='test',
        #                     default=False,
        #                     help='Send as test only.')

    def handle(self, *args, **options):
        file = options["file"][0]
        # test = options['test']

        self.stdout.write("Populating Buildings...")

        with open(file) as buildings_json:
            data = json.load(buildings_json)

        admin = User.objects.filter(username="admin").first()
        for row in data:
            if row["fields"]["u_type"] == "Building":
                building, created = Building.objects.update_or_create(
                    number=row["fields"]["u_code"],
                    defaults={
                        "name": row["fields"]["u_display_name"],
                        "abbreviation": row["fields"]["u_abbreviation"] or None,
                        "city": row["fields"]["city"],
                        "changed_by": admin,
                    },
                )

        cursor = database.execute_sql(
            r"""
            SELECT DISTINCT
            regexp_replace(ports.ifAlias, '^[^/]+/[^/]+/([0-9a-z]+).*', '\\1') AS building_code,
            ports.ifVlan AS vlan_id,
            false AS tagged
            FROM devices join ports on devices.device_id = ports.device_id
            WHERE ports.ifAlias RLIKE '^[^/]+/[^/]+/([0-9a-z]{4,}).*' AND ports.ifName LIKE '%%ethernet%%'
                AND ports.ifAlias not LIKE 'ethernet%%' AND ports.ifVlan not in (1, 4094, 4095)

            UNION

            SELECT DISTINCT
            regexp_replace(ports.ifAlias, '^[^/]+/[^/]+/([0-9a-z]+).*', '\\1') AS building_code,
            ports_vlans.vlan AS vlan_id,
            true AS tagged
            FROM devices JOIN ports ON devices.device_id = ports.device_id
               JOIN ports_vlans ON ports.port_id = ports_vlans.port_id
            WHERE ports.ifAlias RLIKE '^[^/]+/[^/]+/([0-9a-z]{4,}).*' AND ports.ifName LIKE '%%ethernet%%'
                AND ports.ifAlias not LIKE 'ethernet%%' AND ports_vlans.vlan not in (1, 4094, 4095);


        """
        )

        vlan_data = cursor.fetchall()
        building_vlans = {}

        for row in vlan_data:
            if row[0].upper() not in building_vlans:
                building_vlans[row[0].upper()] = []
            building_vlans[row[0].upper()].append([row[1], row[2]])

        for code, vlan in list(building_vlans.items()):
            for item in vlan:
                building = Building.objects.filter(number=code).first()
                vlan = Vlan.objects.filter(vlan_id=item[0]).first()
                if building and vlan:
                    BuildingToVlan.objects.update_or_createe(
                        building=building,
                        vlan=vlan,
                        defaults={
                            "tagged": True if item[1] else False,
                            "changed_by": admin,
                        },
                    )
                else:
                    if not building:
                        self.stdout.write("Building %s does not exist in IPAM" % code)
                    if not vlan:
                        self.stdout.write("Vlan %s does not exist in IPAM" % item[0])
