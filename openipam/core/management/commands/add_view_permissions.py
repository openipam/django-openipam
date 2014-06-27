from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    args = ''
    help = 'Create View Permissions for models.'

    def handle(self, *args, **options):

        # for each of our content types
        for content_type in ContentType.objects.all():
            # build our permission slug
            codename = "view_%s" % content_type.model

            # add it
            Permission.objects.get_or_create(
                content_type=content_type,
                codename=codename,
                name="Can view %s" % content_type.name)

            print "Added view permission for %s" % content_type.name
