from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.dns.views import DNSCreateView, DNSListView, DNSListJson


urlpatterns = patterns('openipam.dns.views',
    url(r'^dnsrecord/add/$', RedirectView.as_view(url=reverse_lazy('list_dns'))),
    url(r'^dnsrecord/\w*$', RedirectView.as_view(url=reverse_lazy('list_dns'))),

    url(r'^$', DNSListView.as_view(), name='list_dns'),
    url(r'^data/$', DNSListJson.as_view(), name='json_dns'),
    url(r'^host:(?P<host>[\w.*-]+)/$', DNSListView.as_view(), name='list_dns'),
    url(r'^host:(?P<host>[\w.*-]+)/data/$', DNSListJson.as_view(), name='json_dns'),
    url(r'^add/$', DNSCreateView.as_view(), name='add_dns'),
)
