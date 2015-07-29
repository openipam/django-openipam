from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.hosts.views import HostListView, HostUpdateView, HostCreateView, \
    HostDetailView, HostListJson, HostAddressCreateView, HostAddressDeleteView, HostBulkCreateView


urlpatterns = patterns('openipam.hosts.views',

    url(r'^host/add/$', RedirectView.as_view(url=reverse_lazy('add_hosts'))),
    url(r'^host/\w*$', RedirectView.as_view(url=reverse_lazy('list_hosts'))),
    url(r'^$', HostListView.as_view(), name='list_hosts'),
    #url(r'^$', 'index', name='hosts'),

    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/remove/$', HostAddressDeleteView.as_view(), name='remove_addresses_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/$', HostAddressCreateView.as_view(), name='add_addresses_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/detail/$', HostDetailView.as_view(), name='view_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$', HostUpdateView.as_view(), name='update_host'),
    url(r'^data/$', HostListJson.as_view(), name='json_hosts'),
    url(r'^add/bulk/$', HostBulkCreateView.as_view(), name='add_hosts_bulk'),
    url(r'^add/$', HostCreateView.as_view(), name='add_hosts'),
    url(r'^owners/$', 'change_owners', name='change_owners'),
    #url(r'^add/$', 'add', name='add_hosts'),
)
