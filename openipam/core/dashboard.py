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
from django.urls import reverse_lazy
from django.db.models.aggregates import Count
from django.contrib.auth import get_user_model
from django.core.cache import cache

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import Host
from openipam.core.modules import HTMLContentModule

from datetime import datetime

import qsstats

User = get_user_model()


class IPAMIndexDashboard(Dashboard):
    """
    Custom index dashboard for openipam.
    """

    title = ""

    def init_with_context(self, context):
        self.site_name = get_admin_site_name(context)
        request = context["request"]

        # append intro module
        self.children.append(
            HTMLContentModule(
                "<strong>Welcome to the openIPAM.</strong>",
                html="""
                    <div style="margin: 10px 20px;">
                        <p>
                            We are now using <a href="%(feature_request_link)s" target="_blank">Issues on GitHub</a>
                            to help aid us with features and bugs.
                            Please make an issue on GitHub to give us feedback.
                        </p>
                        <p>Item to consider when using the new interface:</p>
                        <ul id="new-interface-list">
                            <li>Permissions - Do you have all your permissions?</li>
                            <li>Hosts - Do you see all your hosts?</li>
                            <li>DNS Entries - Do you see all DNS Entries?</li>
                        </ul>
                        <p>If you have any questions, please email:  <a href="mailto:%(email)s">%(email)s</a></p>
                    </div>
            """
                % {
                    "email": CONFIG.get("EMAIL_ADDRESS"),
                    "feature_request_link": "https://github.com/openipam/django-openipam/issues/",
                },
            )
        )

        self.children.append(
            HTMLContentModule(
                "Navigation",
                html="""
                <ul>
                    <li><a href="%(url_hosts)s">List Hosts</a></li>
                    <li><a href="%(url_add_hosts)s">Add Host</a></li>
                    <li><a href="%(url_dns)s">DNS Records</a></li>
                </ul>
                <ul>
                    <li style="border-top: 1px solid #e5e5e5;">
                        <a href="%(url_feature_request)s">Feature or Bug?</a>
                    </li>
                    <li><a href="%(url_profile)s">Profile</a></li>
                </ul>
            """
                % {
                    "url_hosts": reverse_lazy("core:hosts:list_hosts"),
                    "url_add_hosts": reverse_lazy("core:hosts:add_hosts"),
                    "url_dns": reverse_lazy("core:dns:list_dns"),
                    "url_feature_request": reverse_lazy("core:feature_request"),
                    "url_profile": reverse_lazy("core:profile"),
                },
            )
        )

        if request.user.is_staff or request.user.is_superuser:
            # append an app list module for "Administration"
            self.children.append(IPAMAppList(_("Administration"), models=()))

        # append recent stats module
        hosts = Host.objects.all()
        hosts_stats = qsstats.QuerySetStats(
            hosts, "changed", aggregate=Count("mac"), today=datetime.now()
        )
        users = User.objects.all()
        users_stats = qsstats.QuerySetStats(users, "date_joined", today=datetime.now())

        hosts_today = cache.get("hosts_today")
        hosts_week = cache.get("hosts_week")
        hosts_month = cache.get("hosts_month")

        if hosts_today is None:
            hosts_today = hosts_stats.this_day()
            cache.set("hosts_today", hosts_today)
        if hosts_week is None:
            hosts_week = hosts_stats.this_week()
            cache.set("hosts_week", hosts_week)
        if hosts_month is None:
            hosts_month = hosts_stats.this_month()
            cache.set("hosts_month", hosts_month)

        users_today = cache.get("users_today")
        users_week = cache.get("users_week")
        users_month = cache.get("users_month")

        if users_today is None:
            users_today = users_stats.this_day()
            cache.set("users_today", users_today)
        if users_week is None:
            users_week = users_stats.this_week()
            cache.set("users_week", users_week)
        if users_month is None:
            users_month = users_stats.this_month()
            cache.set("users_month", users_month)

        self.children.append(
            HTMLContentModule(
                "Recent Stats",
                html="""
                <div style="margin: 10px 20px;" class="well well-sm">
                    <h5>Hosts</h5>
                    <p><strong>%(hosts_today)s</strong> hosts changed today.</p>
                    <p><strong>%(hosts_week)s</strong> hosts changed this week.</p>
                    <p><strong>%(hosts_month)s</strong> hosts changed this month.</p>
                </div>
                <div style="margin: 10px 20px;" class="well well-sm">
                    <h5>Users</h5>
                    <p><strong>%(users_today)s</strong> users joined today.</p>
                    <p><strong>%(users_week)s</strong> users joined this week.</p>
                    <p><strong>%(users_month)s</strong> users joined this month.</p>
                </div>
            """
                % {
                    "hosts_today": hosts_today,
                    "hosts_week": hosts_week,
                    "hosts_month": hosts_month,
                    "users_today": users_today,
                    "users_week": users_week,
                    "users_month": users_month,
                },
            )
        )

        # append a recent actions module
        self.children.append(modules.RecentActions(_("Recent Actions"), limit=5))


class IPAMAppList(modules.AppList):
    template = "admin_tools/dashboard/modules/ipam_app_list.html"

    def init_with_context(self, context):
        super(IPAMAppList, self).init_with_context(context)


class IPAMAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for openipam.
    """

    models = None
    app_title = None
    # we disable title because its redundant with the model list module
    title = ""

    def __init__(self, app_title, models, **kwargs):
        kwargs.update({"app_title": app_title, "models": models})
        super(IPAMAppIndexDashboard, self).__init__(**kwargs)

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        # request = context['request']
        models = self.models
        exclude = None

        # Hack for DNS App
        if "dns" in self.app_title.lower():
            self.app_title = "Domains & DNS"
        elif "admin" in self.app_title.lower():
            models = ("django.contrib.*",)
            exclude = ("django.contrib.auth.*",)
        elif "auth" in self.app_title.lower():
            models = ("django.contrib.auth.*",)

        self.app_title = self.app_title + " Admin"

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(title=self.app_title, models=models, exclude=exclude)
        ]

        self.children += [
            modules.RecentActions(
                _("Recent Actions"), include_list=self.get_app_content_types(), limit=5
            )
        ]

        return super(IPAMAppIndexDashboard, self).init_with_context(context)
