from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.db.models import Q
from django.contrib.auth.models import User as AuthUser, Group as AuthGroup
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission

from operator import or_
from functools import reduce

from openipam.user.managers import IPAMUserManager
from openipam.user.signals import (
    assign_ipam_groups,
    force_usernames_uppercase,
    remove_obj_perms_connected_with_user,
    add_group_souce,
)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin " "site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    source = models.ForeignKey("AuthSource", db_column="source", blank=True, null=True)

    objects = IPAMUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __unicode__(self):
        return self.username

    @cached_property
    def is_ipamadmin(self):
        if self.is_superuser:
            return True
        else:
            groups = [group.name for group in self.groups.all()]
            return True if "ipam-admins" in groups else False

    @cached_property
    def network_owner_perms(self):
        if self.has_perm("network.is_owner_network"):
            return True
        else:
            from openipam.network.models import Network

            return Network.objects.by_owner(self, use_groups=True, ids_only=True)

    @cached_property
    def domain_owner_perms(self):
        if self.has_perm("dns.is_owner_domain"):
            return True
        else:
            from openipam.dns.models import Domain

            return Domain.objects.by_owner(self, use_groups=True, names_only=True)

    @cached_property
    def host_owner_perms(self):
        if self.has_perm("hosts.is_owner_host"):
            return True
        else:
            from openipam.hosts.models import Host

            return Host.objects.by_owner(self, use_groups=True, ids_only=True)

    @cached_property
    def network_view_perms(self):
        if self.is_ipamadmin or self.has_perm("network.view_network"):
            return True
        else:
            from openipam.network.models import Network

            return Network.objects.by_owner(self, use_groups=True, ids_only=True)

    @cached_property
    def domain_view_perms(self):
        if self.is_ipamadmin or self.has_perm("dns.view_domain"):
            return True
        else:
            from openipam.dns.models import Domain

            return Domain.objects.by_owner(self, use_groups=True, names_only=True)

    def get_auth_user(self):
        try:
            return AuthUser.objects.get(username=self.username)
        except AuthUser.DoesNotExist:
            return None

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_permissions(self):
        user_permission_strings = self.get_all_permissions()
        if len(user_permission_strings) > 0:
            perm_comps = [
                perm_string.split(".", 1) for perm_string in user_permission_strings
            ]
            q_query = reduce(
                or_,
                [
                    Q(content_type__app_label=app_label) & Q(codename=codename)
                    for app_label, codename in perm_comps
                ],
            )
            return Permission.objects.filter(q_query)
        else:
            return Permission.objects.none()

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")


class GroupSource(models.Model):
    group = models.OneToOneField(AuthGroup, primary_key=True, related_name="source")
    source = models.ForeignKey(
        "AuthSource", db_column="source", default=1, related_name="group"
    )

    def __unicode__(self):
        return self.source.name


class AuthSource(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "auth_sources"


# Connect signals
pre_save.connect(force_usernames_uppercase, sender=User)
post_save.connect(assign_ipam_groups, sender=User)
pre_delete.connect(remove_obj_perms_connected_with_user, sender=User)
post_save.connect(add_group_souce, sender=AuthGroup)
