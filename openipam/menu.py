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

        user = context['request'].user
        admin_sites = admin.site._registry
        hosts_models = filter(lambda x: x.__module__ == 'openipam.hosts.models', admin_sites)
        hosts_models = tuple(sorted(['%s.%s' % (model.__module__, model.__name__) for model in hosts_models]))

        dns_models = filter(lambda x: x.__module__ == 'openipam.dns.models', admin_sites)
        dns_models = tuple(sorted(['%s.%s' % (model.__module__, model.__name__) for model in dns_models]))

        network_models = filter(lambda x: x.__module__ == 'openipam.network.models', admin_sites)
        network_models = tuple(sorted(['%s.%s' % (model.__module__, model.__name__) for model in network_models]))

        if user.is_superuser:
            core_menus = [
                items.ModelList('Hosts', hosts_models),
                items.ModelList('DNS', dns_models),
            ]
        else:
            core_menus = [
                items.MenuItem('Hosts', url=reverse('list_hosts')),
                items.MenuItem('DNS', url=reverse('list_dns')),
            ]

        self.children += [
            items.MenuItem(
                _('Home'),
                reverse('admin:index'),
                icon='icon-home icon-white'
            ),
        ]

        self.children += core_menus
        self.children.append(items.ModelList('Network', network_models))

        if user.is_superuser:
            self.children.append(
                items.MenuItem('',
                    children=[
                        items.ModelList('Users & Groups',
                            [
                                'openipam.user.models.User',
                                'django.contrib.auth.models.Group',
                            ]
                        ),
                        items.ModelList('Permissions',
                            [
                                'django.contrib.auth.models.Permission',
                                'guardian.models.UserObjectPermission',
                                'guardian.models.GroupObjectPermission',
                            ]
                        ),
                    ],
                    icon='icon-user icon-white'
                )
            )

        return super(IPAMMenu, self).init_with_context(context)
