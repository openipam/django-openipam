from django.conf.urls import patterns, url, include
from openipam.hosts.views import HostListView, HostUpdateView, HostCreateView, HostDetailView, HostListJson


urlpatterns = patterns('openipam.hosts.views',

    url(r'^$', HostListView.as_view(), name='list_hosts'),
    #url(r'^$', 'index', name='hosts'),

    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/detail/$', HostDetailView.as_view(), name='view_host'),
    url(r'^(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$', HostUpdateView.as_view(), name='update_host'),
    url(r'^data/mine/$', HostListJson.as_view(is_owner=True), name='my_json_hosts'),
    url(r'^data/$', HostListJson.as_view(), name='json_hosts'),
    url(r'^mine/$', HostListView.as_view(is_owner=True), name='my_hosts'),
    url(r'^add/$', HostCreateView.as_view(), name='add_hosts'),
    url(r'^owners/$', 'change_owners', name='change_owners'),
    #url(r'^add/$', 'add', name='add_hosts'),
)
