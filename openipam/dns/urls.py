from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.dns.views import DNSCreateUpdateView, DNSListView, DNSListJson




urlpatterns = patterns('openipam.dns.views',
    url(r'^dnsrecord/add/$', RedirectView.as_view(url=reverse_lazy('add_dns'))),
    url(r'^dnsrecord/(?P<pk>\d+)/$', RedirectView.as_view(pattern_name='edit_dns')),
    url(r'^dnsrecord/$', RedirectView.as_view(url=reverse_lazy('list_dns'))),

    url(r'^$', DNSListView.as_view(), name='list_dns'),
    url(r'^data/$', DNSListJson.as_view(), name='json_dns'),
    url(r'^host:(?P<host>[\w.*-]+)/$', DNSListView.as_view(), name='list_dns'),
    url(r'^(?P<pk>\d+)/$', DNSCreateUpdateView.as_view(), name='edit_dns'),
    url(r'^add/$', DNSCreateUpdateView.as_view(), name='add_dns'),
)
