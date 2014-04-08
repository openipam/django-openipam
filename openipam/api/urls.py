from django.conf.urls import patterns, url, include
from openipam.api.views.base import UserAuthenticated
from openipam.api.views.network import NetworkList, AddressList, DhcpGroupList
from openipam.api.views.hosts import HostList, HostDetail, HostCreate, HostUpdate, HostOwnerList, HostOwnerAdd, \
    HostOwnerDelete, HostAttributeList, HostAddAttribute, HostDeleteAttribute
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register('hosts2', HostViewSet)


urlpatterns = patterns('openipam.api.views',

    #url(r'^', include(router.urls)),

    url(r'^web/networkselects/(?P<address_type_id>\d+)$', 'web.network_selects', name='api_network_select'),
    url(r'^web/', include('autocomplete_light.urls')),

    # Hosts
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/add/$', HostAddAttribute.as_view(), name='api_host_attribute_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/delete/$', HostDeleteAttribute.as_view(), name='api_host_attribute_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/$', HostAttributeList.as_view(), name='api_host_attribute_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/add/$', HostOwnerAdd.as_view(), name='api_host_owners_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/delete/$', HostOwnerDelete.as_view(), name='api_host_owners_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/$', HostOwnerList.as_view(), name='api_host_owners_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/update/$', HostUpdate.as_view(), name='api_host_update'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/$', HostDetail.as_view(), name='api_host_view'),
    url(r'^hosts/add/$', HostCreate.as_view(), name='api_host_add'),
    url(r'^hosts/$', HostList.as_view(), name='api_host_list'),

    url(r'^network/$', NetworkList.as_view(), name='api_network_list'),
    url(r'^address/$', AddressList.as_view(), name='api_address_list'),
    url(r'^dhcpgroup/$', DhcpGroupList.as_view(), name='api_dhcpgroup_list'),

    url(r'^login/has_auth/', UserAuthenticated.as_view(), name='api_has_auth'),
    url(r'^login/jwt_token/', obtain_jwt_token),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
)
