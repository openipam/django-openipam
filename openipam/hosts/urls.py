from django.urls import path, re_path, reverse_lazy
from django.views.generic.base import RedirectView

from openipam.hosts import views


app_name = "hosts"

urlpatterns = [
    path("", views.HostListView.as_view(), name="list_hosts"),
    path("host/add/", RedirectView.as_view(url=reverse_lazy("core:hosts:add_hosts"))),
    path("data/", views.HostListJson.as_view(), name="json_hosts"),
    path("add/bulk/", views.HostBulkCreateView.as_view(), name="add_hosts_bulk"),
    path("add/", views.HostCreateView.as_view(), name="add_hosts"),
    path("owners/", views.change_owners, name="change_owners"),
    path(
        "add/new/",
        views.HostCreateView.as_view(),
        {"new": True},
        name="add_hosts_new",
    ),
    re_path(r"^host/(?P<pk>[0-9a-fA-F:_.-]+)$", views.HostRedirectView.as_view()),
    re_path(
        r"^host/.*$", RedirectView.as_view(url=reverse_lazy("core:hosts:list_hosts"))
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/remove/$",
        views.HostAddressDeleteView.as_view(),
        name="remove_addresses_host",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/$",
        views.HostAddressCreateView.as_view(),
        name="add_addresses_host",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/detail/$",
        views.HostDetailView.as_view(),
        name="view_host",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$",
        views.HostUpdateView.as_view(),
        name="update_host",
    ),
]
