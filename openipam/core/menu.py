"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'openipam.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from admin_tools.menu import items, Menu

from openipam.conf.ipam_settings import CONFIG


class IPAMMenu(Menu):
    """
    Custom Menu for openipam admin site.
    """

    def __init__(self, **kwargs):

        super(IPAMMenu, self).__init__(**kwargs)

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """

        user = context["request"].user
        admin_sites = admin.site._registry
        hosts_models = filter(
            lambda x: x.__module__ == "openipam.hosts.models", admin_sites
        )
        hosts_models = tuple(
            sorted(
                ["%s.%s" % (model.__module__, model.__name__) for model in hosts_models]
            )
        )

        dns_models = filter(
            lambda x: x.__module__ == "openipam.dns.models", admin_sites
        )
        dns_models = tuple(
            sorted(
                ["%s.%s" % (model.__module__, model.__name__) for model in dns_models]
            )
        )

        network_models = filter(
            lambda x: x.__module__ == "openipam.network.models", admin_sites
        )
        network_models = tuple(
            sorted(
                [
                    "%s.%s" % (model.__module__, model.__name__)
                    for model in network_models
                ]
            )
        )

        if user.is_superuser:
            core_menus = [
                items.ModelList("Hosts", hosts_models),
                items.ModelList("DNS", dns_models),
            ]
        elif user.is_staff:
            host_models = items.ModelList("", ["openipam.hosts.*"])
            dns_models = items.ModelList("", ["openipam.dns.*"])

            host_items = items.MenuItem("Hosts", url=reverse("list_hosts"))
            dns_items = items.MenuItem("DNS", url=reverse("list_dns"))

            if len(dns_models._visible_models(context["request"])) > 1:
                dns_items.children = [
                    items.MenuItem("DNS", url=reverse("list_dns")),
                    items.ModelList(
                        "",
                        ["openipam.dns.*"],
                        exclude=("openipam.dns.models.DnsRecord",),
                    ),
                ]

            if len(host_models._visible_models(context["request"])) > 1:
                host_items.children = [
                    items.MenuItem("Hosts", url=reverse("list_hosts")),
                    items.ModelList(
                        "",
                        models=["openipam.hosts.*"],
                        exclude=("openipam.hosts.models.Host",),
                    ),
                ]

            core_menus = [host_items, dns_items]
        else:
            core_menus = [
                items.MenuItem("Hosts", url=reverse("list_hosts")),
                items.MenuItem("DNS", url=reverse("list_dns")),
            ]

        self.children += [
            items.MenuItem(
                _("Home"),
                reverse("admin:index"),
                icon="glyphicon glyphicon-home icon-white",
            )
        ]

        self.children += core_menus
        self.children.append(items.ModelList("Network", network_models))

        if user.is_superuser:
            self.children.append(
                items.MenuItem(
                    "Admin",
                    children=[
                        items.ModelList(
                            "Users & Groups",
                            [
                                "openipam.user.models.User",
                                "django.contrib.auth.models.Group",
                                "rest_framework.authtoken.models.Token",
                            ],
                        ),
                        items.ModelList(
                            "Permissions",
                            [
                                "django.contrib.auth.models.Permission",
                                "guardian.models.UserObjectPermission",
                                "guardian.models.GroupObjectPermission",
                                "taggit.models.Tag",
                            ],
                        ),
                        items.ModelList(
                            "Logs",
                            [
                                "django.contrib.admin.models.LogEntry",
                                "openipam.log.models.HostLog",
                                "openipam.log.models.EmailLog",
                                "openipam.log.models.DnsRecordsLog",
                                "openipam.log.models.AddressLog",
                                "openipam.log.models.UserLog",
                            ],
                        ),
                        items.ModelList(
                            "Feature Requests", ["openipam.core.models.FeatureRequest"]
                        ),
                    ],
                    # icon='icon-user icon-white'
                )
            )

        elif user.is_staff:
            user_apps = items.AppList(
                "", exclude=("openipam.hosts.*", "openipam.dns.*")
            )
            user_apps.init_with_context(context)

            # if user.has_perm("user.view_user"):
            #     self.children.append(
            #         items.MenuItem("User Manager", url=reverse("user_manager"))
            #     )

            if user_apps.children:
                self.children.append(
                    items.MenuItem(
                        "Admin",
                        children=[
                            items.AppList(
                                "", exclude=("openipam.hosts.*", "openipam.dns.*")
                            )
                        ],
                    )
                )

        if user.is_ipamadmin or user.groups.filter(
            name=CONFIG.get("REPORT_USER_GROUP")
        ):
            self.children.append(
                IPAMMenuItem("Reports", url=reverse("reports_dashboard"))
            )

        return super(IPAMMenu, self).init_with_context(context)


class IPAMMenuItem(items.MenuItem):
    template = "admin_tools/menu/ipamitem.html"

    def __init__(self, title=None, url=None, target=None, **kwargs):
        if target is not None:
            self.target = target

        super(IPAMMenuItem, self).__init__(title, url, **kwargs)
