"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'openipam.menu.CustomMenu'
"""

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from openipam.core import items
from openipam.conf.ipam_settings import CONFIG


class Menu(object):
    """
    This is the base class for creating custom navigation menus.
    A menu can have the following properties:

    ``template``
        A string representing the path to template to use to render the menu.
        As for any other template, the path must be relative to one of the
        directories of your ``TEMPLATE_DIRS`` setting.
        Default value: "admin_tools/menu/menu.html".

    ``children``
        A list of children menu items. All children items mus be instances of
        the :class:`~admin_tools.menu.items.MenuItem` class.

    If you want to customize the look of your menu and it's menu items, you
    can declare css stylesheets and/or javascript files to include when
    rendering the menu, for example::

        from admin_tools.menu import Menu

        class MyMenu(Menu):
            class Media:
                css = {'all': ('css/mymenu.css',)}
                js = ('js/mymenu.js',)

    Here's a concrete example of a custom menu::

        from django.core.urlresolvers import reverse
        from admin_tools.menu import items, Menu

        class MyMenu(Menu):
            def __init__(self, **kwargs):
                super(MyMenu, self).__init__(**kwargs)
                self.children += [
                    items.MenuItem('Home', reverse('admin:index')),
                    items.AppList('Applications'),
                    items.MenuItem('Multi level menu item',
                        children=[
                            items.MenuItem('Child 1', '/foo/'),
                            items.MenuItem('Child 2', '/bar/'),
                        ]
                    ),
                ]

    Below is a screenshot of the resulting menu:

    .. image:: images/menu_example.png
    """

    template = "core/menu/menu.html"
    children = None

    class Media:
        css = ()
        js = ()

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = kwargs.get("children", [])

    def init_with_context(self, context):
        """
        Sometimes you may need to access context or request variables to build
        your menu, this is what the ``init_with_context()`` method is for.
        This method is called just before the display with a
        ``django.template.RequestContext`` as unique argument, so you can
        access to all context variables and to the ``django.http.HttpRequest``.
        """
        pass


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
        hosts_models = [
            x for x in admin_sites if x.__module__ == "openipam.hosts.models"
        ]
        hosts_models = tuple(
            sorted(
                [
                    (
                        model.__name__,
                        "admin:%s_%s_changelist"
                        % (model._meta.app_label, model._meta.model_name),
                    )
                    for model in hosts_models
                ]
            )
        )
        hosts_models = [
            items.ModelList("%s" % model[0], url=reverse("%s" % model[1]))
            for model in hosts_models
        ]

        dns_models = [x for x in admin_sites if x.__module__ == "openipam.dns.models"]
        dns_models = tuple(
            sorted(
                [
                    (
                        model.__name__,
                        "admin:%s_%s_changelist"
                        % (model._meta.app_label, model._meta.model_name),
                    )
                    for model in dns_models
                ]
            )
        )
        dns_models = [
            items.MenuItem("%s" % model[0], url=reverse("%s" % model[1]))
            for model in dns_models
        ]

        network_models = [
            x for x in admin_sites if x.__module__ == "openipam.network.models"
        ]
        network_models = tuple(
            sorted(
                [
                    "%s.%s" % (model.__module__, model.__name__)
                    for model in network_models
                ]
            )
        )

        core_menus = []

        if user.is_superuser:
            # host_items = items.MenuItem("Hosts", url=reverse("hosts:list"))
            # dns_items = items.MenuItem("DNS", url=reverse("dns:list"))

            # dns_items.children = [
            #     items.MenuItem("DNS", url=reverse("dns:list"))
            # ] + dns_models

            # host_items.children = [
            #     items.MenuItem("Hosts", url=reverse("hosts:list"))
            # ] + hosts_models

            # core_menus = [host_items, dns_items]
            self.children += [
                items.MenuItem(
                    "Hosts & Tickets",
                    children=[
                        items.ModelList(
                            "Host Info",
                            [
                                "openipam.hosts.models.Host",
                                "openipam.hosts.models.GuestTicket",
                                "openipam.hosts.models.Disabled",
                            ],
                        ),
                        items.ModelList(
                            "Attributes",
                            [
                                "openipam.hosts.models.Attribute",
                                "openipam.hosts.models.StructuredAttributeValue",
                            ],
                        ),
                        items.ModelList(
                            "Host Admin",
                            [
                                "openipam.hosts.models.Notification",
                                "openipam.hosts.models.ExpirationType",
                                "openipam.hosts.models.OUI",
                            ],
                        ),
                    ],
                )
            ]
        elif user.is_staff:
            host_models = items.ModelList("", ["openipam.hosts.*"])
            dns_models = items.ModelList("", ["openipam.dns.*"])

            host_items = items.MenuItem("Hosts", url=reverse("hosts:list"))
            dns_items = items.MenuItem("DNS", url=reverse("dns:list"))

            if len(dns_models._visible_models(context["request"])) > 1:
                dns_items.children = [
                    items.MenuItem("DNS", url=reverse("dns:list")),
                    items.ModelList(
                        "",
                        ["openipam.dns.*"],
                        exclude=("openipam.dns.models.DnsRecord",),
                    ),
                ]

            if len(host_models._visible_models(context["request"])) > 1:
                host_items.children = [
                    items.MenuItem("Hosts", url=reverse("hosts:list")),
                    items.ModelList(
                        "",
                        models=["openipam.hosts.*"],
                        exclude=("openipam.hosts.models.Host",),
                    ),
                ]

            core_menus = [host_items, dns_items]
        else:
            core_menus = [
                items.MenuItem("Hosts", url=reverse("hosts:list")),
                items.MenuItem("DNS", url=reverse("dns:list")),
            ]

        self.children += [items.Bookmarks(_("Bookmarks"))]

        if core_menus:
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
                                "openipam.user.models.Group",
                                "openipam.user.models.Token",
                            ],
                        ),
                        items.ModelList(
                            "Permissions",
                            [
                                "openipam.user.models.Permission",
                                # "django.contrib.auth.models.Permission",
                                "openipam.user.models.UserObjectPermission",
                                "openipam.user.models.GroupObjectPermission",
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
            #         items.MenuItem("Users", url=reverse("user:list"))
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
                items.MenuItem("Reports", url=reverse("report:dashboard"))
            )

        return super(IPAMMenu, self).init_with_context(context)
