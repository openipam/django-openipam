from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView

from openipam.hosts import views

urlpatterns = [
    url(r'^host/add/$', RedirectView.as_view(url=reverse_lazy('add_hosts'))),
    url(r'^host/\w*$', RedirectView.as_view(url=reverse_lazy('list_hosts'))),
    url(r'^$', views.HostListView.as_view(), name='list_hosts'),
    # url(r'^$', 'index', name='hosts'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/remove/$', views.HostAddressDeleteView.as_view(), name='remove_addresses_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/addresses/$', views.HostAddressCreateView.as_view(), name='add_addresses_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/detail/$', views.HostDetailView.as_view(), name='view_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$', views.HostUpdateView.as_view(), name='update_host'),
    url(r'^data/$', views.HostListJson.as_view(), name='json_hosts'),
    url(r'^add/bulk/$', views.HostBulkCreateView.as_view(), name='add_hosts_bulk'),
    url(r'^add/new/$', views.HostCreateView.as_view(), {'new': True}, name='add_hosts_new'),
    url(r'^add/$', views.HostCreateView.as_view(), name='add_hosts'),
    url(r'^owners/$', views.change_owners, name='change_owners'),
    # url(r'^add/$', 'add', name='add_hosts'),
]
