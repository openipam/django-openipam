from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.dns import views

urlpatterns = [
    url(r"^dnsrecord/add/$", RedirectView.as_view(url=reverse_lazy("add_dns"))),
    url(r"^dnsrecord/(?P<pk>\d+)/$", RedirectView.as_view(pattern_name="edit_dns")),
    url(r"^dnsrecord/$", RedirectView.as_view(url=reverse_lazy("list_dns"))),
    url(r"^$", views.DNSListView.as_view(), name="list_dns"),
    url(r"^data/$", views.DNSListJson.as_view(), name="json_dns"),
    url(r"^host:(?P<host>[\w.*-]+)/$", views.DNSListView.as_view(), name="list_dns"),
    url(r"^(?P<pk>\d+)/$", views.DNSCreateUpdateView.as_view(), name="edit_dns"),
    url(r"^add/$", views.DNSCreateUpdateView.as_view(), name="add_dns"),
]
