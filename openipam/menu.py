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

        #admin_sites = admin.site._registry
        #hosts_models = filter(lambda x: x.__module__ == 'openipam.hosts.models', admin_sites)
        #hosts_models = tuple(sorted(['%s.%s' % (model.__module__, model.__name__) for model in hosts_models]))

        #assert False, hosts_models

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
            ),
            items.MenuItem('',
                children = [
                    items.AppList('',
                        models = (
                            'openipam.dns.*',
                            'openipam.network.*',
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
