from django.conf.urls import patterns, url, include
from openipam.dns.views import DNSCreateView, DNSListView


urlpatterns = patterns('openipam.dns.views',
    #url(r'^add/$', DNSCreateView.as_view(), name='add_dns'),
    url(r'^$', 'dns_list_edit', name='list_dns'),
    #url(r'^$', DNSListView.as_view(), name='list_dns'),
    #url(r'^$', 'index', name='dns'),
)




