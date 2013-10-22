from django.db import models


class UserToGroupManager(models.Manager):

    def get_queryset(self):
        return super(UserToGroupManager, self).get_queryset().select_related().all()
