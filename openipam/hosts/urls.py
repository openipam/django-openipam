from django.conf.urls import patterns, url, include
from openipam.hosts.views import HostListView, HostUpdateView


urlpatterns = patterns('openipam.hosts.views',

    url(r'^$', HostListView.as_view(), name='list_hosts'),
    #url(r'^$', 'index', name='hosts'),

    url(r'^(?P<pk>([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2})/$', HostUpdateView.as_view(), name='update_host'),
    url(r'^mine/$', HostListView.as_view(is_owner=True), name='my_hosts'),
    url(r'^add/$', 'add', name='add_hosts'),
)




