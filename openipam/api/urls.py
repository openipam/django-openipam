from django.conf.urls import patterns, url, include
from openipam.api.views.network import NetworkList, AddressList, DhcpGroupList
from openipam.api.views.hosts import HostList, HostDetail, HostCreate
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = patterns('openipam.api.views',

    url(r'^web/networkselects/(?P<address_type_id>\d+)$', 'web.network_selects', name='api_network_select'),
    url(r'^web/', include('autocomplete_light.urls')),

    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}){5}[0-9a-fA-F]{2})/$', HostDetail.as_view(), name='api_host_view'),
    url(r'^hosts/add/$', HostCreate.as_view(), name='api_host_add'),
    url(r'^hosts/$', HostList.as_view(), name='api_host_list'),

    url(r'^network/$', NetworkList.as_view(), name='api_network_list'),
    url(r'^address/$', AddressList.as_view(), name='api_address_list'),
    url(r'^dhcpgroup/$', DhcpGroupList.as_view(), name='api_dhcpgroup_list'),

    url(r'^login/jwt_token/', obtain_jwt_token),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
)
