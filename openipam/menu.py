"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'openipam.menu.CustomMenu'
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class IPAMMenu(Menu):
    """
    Custom Menu for openipam admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(
                _('Admin Dashboard'),
                reverse('admin:index'),
                icon='icon-home icon-white'
            ),
            #items.Bookmarks(icon='icon-heart icon-white'),
            items.MenuItem('',
                children = [
                    items.ModelList('Users & Groups',
                        [
                            'openipam.user.models.User',
                            'django.contrib.auth.*',
                            'openipam.hosts.models.HostUserObjectPermission',
                            'openipam.hosts.models.HostGroupObjectPermission',
                            'openipam.dns.models.DomainGroupObjectPermission',
                            'openipam.dns.models.DomainUserObjectPermission',
                        ]
                    ),
                ],
                icon='icon-user icon-white'
            ),
            items.MenuItem('',
                children = [
                    items.AppList('',
                        models = (
                            'openipam.dns.*',
                            'openipam.network.*',
                            'openipam.hosts.*',
                        )
                    ),
                ],
                icon='icon-globe icon-white'
            ),
            # items.AppList(
            #     _('Administration'),
            #     models=(
            #         'openipam.user.models.User',
            #         'django.contrib.*',
            #     ),
            #     icon='icon-cog icon-white'
            # )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(IPAMMenu, self).init_with_context(context)
