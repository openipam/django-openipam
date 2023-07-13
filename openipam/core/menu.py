"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'openipam.menu.CustomMenu'
"""

from django.urls import reverse
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
        hosts_models = [x for x in admin_sites if x.__module__ == "openipam.hosts.models"]
        hosts_models = tuple(sorted(["%s.%s" % (model.__module__, model.__name__) for model in hosts_models]))

        dns_models = [x for x in admin_sites if x.__module__ == "openipam.dns.models"]
        dns_models = tuple(sorted(["%s.%s" % (model.__module__, model.__name__) for model in dns_models]))

        network_models = [x for x in admin_sites if x.__module__ == "openipam.network.models"]
        network_models = tuple(sorted(["%s.%s" % (model.__module__, model.__name__) for model in network_models]))

        formattedHosts = [x.__name__ for x, y in items.ModelList("", hosts_models)._visible_models(context["request"])]

        hostMenu = items.MenuItem(
            "Hosts",
            children=[
                items.ModelList(x.title, list(filter(lambda y: y not in formattedHosts, x.models)))
                for x in [
                    items.ModelList(
                        "Hosts",
                        [
                            "openipam.hosts.models.Host",
                            "openipam.hosts.models.Disabled",
                            "openipam.hosts.models.ExpirationType",
                        ],
                    ),
                    items.ModelList(
                        "Attributes",
                        [
                            "openipam.hosts.models.StructuredAttributeValue",
                            "openipam.hosts.models.Attribute",
                        ],
                    ),
                    items.ModelList(
                        "Notifications",
                        [
                            "openipam.hosts.models.Notification",
                        ],
                    ),
                    items.ModelList(
                        "Guest Tickets",
                        [
                            "openipam.hosts.models.GuestTicket",
                        ],
                    ),
                ]
            ],
        )

        formattedDNS = [x.__name__ for x, y in items.ModelList("", dns_models)._visible_models(context["request"])]
        dnsMenu = items.MenuItem(
            "DNS",
            children=[
                items.ModelList(x.title, list(filter(lambda y: y not in formattedDNS, x.models)))
                for x in [
                    items.ModelList(
                        "DNS",
                        [
                            "openipam.dns.models.DnsRecord",
                            "openipam.dns.models.DnsType",
                            "openipam.dns.models.DnsView",
                        ],
                    ),
                    items.ModelList(
                        "DHCP",
                        [
                            "openipam.dns.models.DhcpDnsRecord",
                            "openipam.dns.models.Domain",
                        ],
                    ),
                ]
            ],
        )

        formattedNetwork = [
            x.__name__ for x, y in items.ModelList("", network_models)._visible_models(context["request"])
        ]
        networkMenu = items.MenuItem(
            "Network",
            children=[
                items.ModelList(x.title, list(filter(lambda y: y not in formattedNetwork, x.models)))
                for x in [
                    items.ModelList(
                        "Networks",
                        [
                            "openipam.network.models.Network",
                            "openipam.network.models.NetworkRange",
                            "openipam.network.models.NetworkToVlan",
                            "openipam.network.models.SharedNetwork",
                        ],
                    ),
                    items.ModelList(
                        "Addresses",
                        [
                            "openipam.network.models.Address",
                            "openipam.network.models.AddressType",
                        ],
                    ),
                    items.ModelList(
                        "DHCP",
                        [
                            "openipam.network.models.DhcpOption",
                            "openipam.network.models.DhcpGroup",
                            "openipam.network.models.DhcpOptionToDhcpGroup",
                            "openipam.network.models.Lease",
                        ],
                    ),
                    items.ModelList(
                        "Buildings",
                        [
                            "openipam.network.models.Building",
                            "openipam.network.models.BuildingToVlan",
                        ],
                    ),
                    items.ModelList(
                        "Pools",
                        [
                            "openipam.network.models.Pool",
                            "openipam.network.models.DefaultPool",
                        ],
                    ),
                    items.ModelList(
                        "Vlans",
                        [
                            "openipam.network.models.Vlan",
                        ],
                    ),
                ]
            ],
        )

        self.children += [
            items.MenuItem(
                _("Home"),
                reverse("admin:index"),
                icon="glyphicon glyphicon-home icon-white",
            )
        ]

        self.children += [hostMenu, dnsMenu]
        if formattedNetwork:
            self.children += [networkMenu]

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
                        items.ModelList("Feature Requests", ["openipam.core.models.FeatureRequest"]),
                    ],
                    # icon='icon-user icon-white'
                )
            )

        elif user.is_staff:
            user_apps = items.AppList("", exclude=("openipam.hosts.*", "openipam.dns.*"))
            user_apps.init_with_context(context)

            # if user.has_perm("user.view_user"):
            #     self.children.append(
            #         items.MenuItem("User Manager", url=reverse("user_manager"))
            #     )

            if user_apps.children:
                self.children.append(
                    items.MenuItem(
                        "Admin",
                        children=[items.AppList("", exclude=("openipam.hosts.*", "openipam.dns.*"))],
                    )
                )

        if user.is_ipamadmin or user.groups.filter(name=CONFIG.get("REPORT_USER_GROUP")):
            self.children.append(
                items.MenuItem(
                    "Reports",
                    children=[
                        items.MenuItem(
                            title="openIPAM Stats",
                            url=reverse("core:report:reports_ipam_stats"),
                        ),
                        items.MenuItem(
                            title="Hardcoded Disabled Hosts",
                            url=reverse("core:report:reports_disabled"),
                        ),
                        items.MenuItem(
                            title="Exposed Hosts",
                            url=reverse("core:report:reports_exposed_hosts"),
                        ),
                        items.MenuItem(
                            title="Host with no DNS Records",
                            url=reverse("core:report:reports_host_dns"),
                        ),
                        items.MenuItem(
                            title="Broken PTR Records",
                            url=reverse("core:report:reports_ptr_dns"),
                        ),
                        items.MenuItem(
                            title="Expired Hosts",
                            url=reverse("core:report:expired_hosts"),
                        ),
                        items.MenuItem(
                            title="Orphaned DNS",
                            url=reverse("core:report:orphaned_dns"),
                        ),
                    ],
                    # icon='icon-user icon-white'
                )
            )

        return super(IPAMMenu, self).init_with_context(context)


class IPAMMenuItem(items.MenuItem):
    template = "admin_tools/menu/ipamitem.html"

    def __init__(self, title=None, url=None, target=None, **kwargs):
        if target is not None:
            self.target = target

        super(IPAMMenuItem, self).__init__(title, url, **kwargs)
