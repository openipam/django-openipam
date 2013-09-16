from django.conf.urls import patterns, url, include
from openipam.api.views.network import NetworkList, AddressList, DhcpGroupList


urlpatterns = patterns('openipam.api.views',

    url(r'^web/networkselects/(?P<address_id>\d+)$', 'web.network_selects', name='network_select'),


    url(r'^network/$', NetworkList.as_view(), name='network_list'),
    url(r'^address/$', AddressList.as_view(), name='address_list'),
    url(r'^dhcpgroup/$', DhcpGroupList.as_view(), name='dhcpgroup_list'),
)
