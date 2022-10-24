from django.urls import path, re_path, reverse_lazy
from django.views.generic.base import RedirectView

from openipam.dns import views


app_name = "dns"

urlpatterns = [
    path("", views.DNSListView.as_view(), name="list_dns"),
    path("add/", views.DNSCreateUpdateView.as_view(), name="add_dns"),
    path("data/", views.DNSListJson.as_view(), name="json_dns"),
    path("<int:pk>/", views.DNSCreateUpdateView.as_view(), name="edit_dns"),
    path("dnsrecord/add/", RedirectView.as_view(url=reverse_lazy("add_dns"))),
    path("dnsrecord/<int:pk>/", RedirectView.as_view(pattern_name="edit_dns")),
    path("dnsrecord/", RedirectView.as_view(url=reverse_lazy("list_dns"))),
    re_path(
        r"^host:(?P<host>[\w.*-]+)/$", views.DNSListView.as_view(), name="list_dns"
    ),
]
