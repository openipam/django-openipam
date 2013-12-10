"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'openipam.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'openipam.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.text import capfirst

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from admin_tools.menu import items, Menu
from admin_tools.menu.items import MenuItem
from django.contrib import admin


class IPAMIndexDashboard(Dashboard):
    """
    Custom index dashboard for openipam.
    """

    title = ''


    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"

        # self.children.append(modules.LinkList(
        #     _('Quick links'),
        #     layout='inline',
        #     draggable=False,
        #     deletable=False,
        #     collapsible=False,
        #     children=[
        #         [_('Return to site'), '/'],
        #         [_('Change password'),
        #          reverse('%s:password_change' % site_name)],
        #         [_('Log out'), reverse('%s:logout' % site_name)],
        #     ]
        # ))

        #append an app list module for "IPAM"
        self.children.append(modules.ModelList(
            _('Hosts'),
            models=(
                'openipam.hosts.*',
            ),
        ))

        self.children.append(modules.ModelList(
            _('Network'),
            models=(
                'openipam.network.*',
            ),
        ))

        self.children.append(modules.ModelList(
            _('Domains & DNS'),
            models=(
                'openipam.dns.*',
            ),
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            models=(
            'openipam.user.models.User',
            'django.contrib.*',
            'guardian.*',
            'openipam.core.*',
            ),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,

        ))

        self.children.append(modules.ModelList(
            _('TO BE DELETED'),
            models=(
                'openipam.user.models.Permission',
                'openipam.user.models.Group',
                'openipam.user.models.UserToGroup',
                'openipam.user.models.HostToGroup',
                'openipam.user.models.DomainToGroup',
                'openipam.user.models.NetworkToGroup',
                'openipam.user.models.PoolToGroup',
            ),
        ))


class IPAMAppList(modules.AppList):

    def init_with_context(self, context):
        super(IPAMAppList, self).init_with_context(context)
        #assert False, self.children


class IPAMAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for openipam.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        #Hack for DNS App
        if 'dns' in self.app_title.lower():
            self.app_title = 'Domains & DNS'

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(
                self.app_title,
                sorted(self.models)
            ),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(IPAMAppIndexDashboard, self).init_with_context(context)
