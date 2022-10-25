from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from openipam.report import views

app_name = "report"

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("core:report:reports_ipam_stats"))),
    path("disabled/", views.DisabledHostsView.as_view(), name="reports_disabled"),
    path(
        "exposed_hosts/",
        views.ExposedHostsView.as_view(),
        name="reports_exposed_hosts",
    ),
    path("host_dns/", views.HostDNSView.as_view(), name="reports_host_dns"),
    path("ptr_dns/", views.PTRDNSView.as_view(), name="reports_ptr_dns"),
    path("ipam_stats/", views.IpamStatsView.as_view(), name="reports_ipam_stats"),
    path("expired_hosts/", views.ExpiredHostsView.as_view(), name="expired_hosts"),
]
