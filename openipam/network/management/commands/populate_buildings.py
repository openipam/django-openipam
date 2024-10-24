from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model

from openipam.network.models import Building


User = get_user_model()


class Command(BaseCommand):
    args = ""
    help = "Populate building vlan data."

    def handle(self, *args, **options):
        self.stdout.write("Populating Buildings...")

        def get_buildings_sql():
            def dictfetchall(cursor):
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * from e911.e911_location where u_type = 'Building';"
                )
                building_data = dictfetchall(cursor)
            return building_data

        admin = User.objects.filter(username="admin").first()
        created_buildings = 0

        for row in get_buildings_sql():
            building, created = Building.objects.update_or_create(
                number=row["u_code"],
                defaults={
                    "name": row["u_display_name"],
                    "abbreviation": row["u_abbreviation"] or None,
                    "city": row["city"],
                    "changed_by": admin,
                },
            )
            if created:
                self.stdout.write("Created: %s" % building.name)
                created_buildings += 1
            else:
                self.stdout.write("Updated: %s" % building.name)

        self.stdout.write("%s buildings created" % created_buildings)
