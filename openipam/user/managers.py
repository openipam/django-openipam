from django.db import models
from django.contrib.auth.models import UserManager


class UserToGroupManager(models.Manager):

    def get_queryset(self):
        return super(UserToGroupManager, self).get_queryset().select_related().all()

    def delete(self():
        self.update(is_active=False)


class IPAMUserManager(UserManager):

    def get_queryset(self):
        return super(IPAMUserManager, self).get_queryset().prefetch_related('groups').all()

    def get_ipam_admins(self):
        return self.filter(groups__name='ipam-admins')
