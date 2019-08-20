from django.urls import path, re_path
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.dns import views

app_name = "dns"

urlpatterns = [
    path("", views.DNSListView.as_view(), name="list"),
    path("dnsrecord/add/", RedirectView.as_view(url=reverse_lazy("dns:add"))),
    path("dnsrecord/<int:pk>/", RedirectView.as_view(pattern_name="edit")),
    path("dnsrecord/", RedirectView.as_view(url=reverse_lazy("dns:list"))),
    path("data/", views.DNSListJson.as_view(), name="json"),
    re_path(r"^host:(?P<host>[\w.*-]+)/$", views.DNSListView.as_view(), name="list"),
    path("<int:pk>/", views.DNSCreateUpdateView.as_view(), name="edit"),
    path("add/", views.DNSCreateUpdateView.as_view(), name="add"),
]
