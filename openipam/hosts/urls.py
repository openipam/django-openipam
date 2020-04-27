from django.urls import path, re_path
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.hosts import views

app_name = "hosts"

urlpatterns = [
    path("", views.HostListView.as_view(), name="list"),
    re_path(r"^host/add/?$", RedirectView.as_view(url=reverse_lazy("hosts:add"))),
    re_path(r"^host/(?P<pk>[0-9a-fA-F:_.-]+)$", views.HostRedirectView.as_view()),
    re_path(r"^host/.*$", RedirectView.as_view(url=reverse_lazy("hosts:list"))),
    # path(r'^$', 'index', name='hosts'),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/remove/$",
        views.HostAddressDeleteView.as_view(),
        name="remove_addresses",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/$",
        views.HostAddressCreateView.as_view(),
        name="add_addresses",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/detail/$",
        views.HostDetailView.as_view(),
        name="detail",
    ),
    re_path(
        r"^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$",
        views.HostUpdateView.as_view(),
        name="update",
    ),
    path("data/", views.HostListJson.as_view(), name="json"),
    path("add/bulk/", views.HostBulkCreateView.as_view(), name="add_bulk"),
    path("add/new/", views.HostCreateView.as_view(), {"new": True}, name="add_new"),
    path("add/", views.HostCreateView.as_view(), name="add"),
    path("owners/", views.change_owners, name="change_owners"),
]
