from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.report import views


urlpatterns = [
    url(r"^disabled/$", views.DisabledHostsView.as_view(), name="reports_disabled"),
    url(
        r"^exposed_hosts/$",
        views.ExposedHostsView.as_view(),
        name="reports_exposed_hosts",
    ),
    url(r"^host_dns/$", views.HostDNSView.as_view(), name="reports_host_dns"),
    url(r"^ptr_dns/$", views.PTRDNSView.as_view(), name="reports_ptr_dns"),
    url(r"^ipam_stats/$", views.IpamStatsView.as_view(), name="reports_ipam_stats"),
    url(r"^expired_hosts/$", views.ExpiredHostsView.as_view(), name="expired_hosts"),
    url(r"^orphaned_dns/$", views.OrphanedDNSView.as_view(), name="orphaned_dns"),
    url(r"^$", RedirectView.as_view(url=reverse_lazy("reports_ipam_stats"))),
]
