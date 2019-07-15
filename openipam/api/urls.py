from django.conf.urls import url, include

from rest_framework_jwt.views import obtain_jwt_token

from rest_framework.routers import SimpleRouter, Route

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from openipam.api import views


schema_view = get_schema_view(
    openapi.Info(
        title="OpenIPAM API", default_version="v1", description="Test description"
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)


class OPENIPAMAPIRouter(SimpleRouter):
    """
    A router to match existing url patterns
    """

    routes = [
        Route(
            url=r"^{prefix}/$",
            mapping={"get": "list"},
            name="api_{basename}_list",
            initkwargs={"suffix": "List"},
        ),
        Route(
            url=r"^{prefix}/add/$",
            mapping={"post": "create"},
            name="api_{basename}_create",
            initkwargs={"suffix": "Create"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/$",
            mapping={"get": "retrieve"},
            name="api_{basename}_detail",
            initkwargs={"suffix": "Detail"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/update/$",
            mapping={"get": "retrieve", "post": "update", "put": "update"},
            name="api_{basename}_update",
            initkwargs={"suffix": "Update"},
        ),
        Route(
            url=r"^{prefix}/{lookup}/delete/$",
            mapping={"get": "retrieve", "delete": "destroy", "post": "destroy"},
            name="api_{basename}_delete",
            initkwargs={"suffix": "Delete"},
        ),
    ]


router = OPENIPAMAPIRouter()
router.register("dhcpgroup", views.network.DhcpGroupViewSet)
router.register("dhcpoption", views.network.DhcpOptionViewSet)
router.register("dhcpoptiontodhcpgroup", views.network.DhcpOptionToDhcpGroupViewSet)
router.register("sharednetworks", views.network.SharedNetworkViewSet)
router.register("networkranges", views.network.NetworkRangeViewSet)
router.register("networktovlan", views.network.NetworkToVlanViewSet)
router.register("pools", views.network.PoolViewSet)
router.register("defaultpools", views.network.DefaultPoolViewSet)
router.register("vlans", views.network.VlanViewSet)

urlpatterns = [
    url(r"^", include(router.urls)),
    url(
        r"^web/show_users/(?P<group_id>\d+)$",
        views.web.show_users,
        name="api_show_users",
    ),
    url(
        r"^web/networkselects/(?P<address_type_id>\d+)$",
        views.web.network_selects,
        name="api_network_select",
    ),
    url(
        r"^web/structuredattributevalues/(?P<attribute_id>\d+)$",
        views.web.structured_attribute_selects,
        name="api_structured_attribute_select",
    ),
    url(r"^web/", include("autocomplete_light.urls")),
    # Reports
    url(
        r"^reports/serverhosts/$",
        views.report.ServerHostView.as_view(),
        name="api_reports_server_hosts",
    ),
    url(
        r"^reports/leaseusage/$",
        views.report.LeaseUsageView.as_view(),
        name="api_reports_lease_usage",
    ),
    url(
        r"^reports/leasegraph/(?P<network>.*)/$",
        views.report.LeaseGraphView.as_view(),
        name="api_reports_lease_graph",
    ),
    url(
        r"^reports/weathermap/$",
        views.report.WeatherMapView.as_view(),
        name="api_reports_weather_map",
    ),
    url(
        r"^reports/weathermap/config\.json$",
        views.report.weathermap_config,
        name="api_reports_weather_map_config",
    ),
    url(
        r"^reports/buildingmap/config\.json$",
        views.report.buildingmap_config,
        name="api_reports_buildingmap_config",
    ),
    url(
        r"^reports/chartstats/$",
        views.report.StatsAPIView.as_view(),
        name="api_reports_chart_stats",
    ),
    url(
        r"^reports/dashboard/$",
        views.report.DashboardAPIView.as_view(),
        name="api_reports_dashboard",
    ),
    # Users
    url(r"^users/$", views.users.UserList.as_view(), name="api_users_list"),
    # Groups
    url(r"^groups/$", views.users.GroupList.as_view(), name="api_groups_list"),
    url(
        r"^groups/options/$",
        views.users.GroupOptionsList.as_view(),
        name="api_groupsoptions_list",
    ),
    # Attributes
    url(r"^attributes/$", views.hosts.AttributeList.as_view(), name="api_attributes"),
    url(
        r"^attributes/structured/values/$",
        views.hosts.StructuredAttributeValueList.as_view(),
        name="api_attributes_structured_values",
    ),
    # Hosts
    url(
        r"^hosts/mac/next/$",
        views.hosts.HostNextMac.as_view(),
        name="api_host_mac_next",
    ),
    url(r"^hosts/mac/$", views.hosts.HostMac.as_view(), name="api_host_mac"),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/add/$",
        views.hosts.HostAddAttribute.as_view(),
        name="api_host_attribute_add",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/delete/$",
        views.hosts.HostDeleteAttribute.as_view(),
        name="api_host_attribute_delete",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/$",
        views.hosts.HostAttributeList.as_view(),
        name="api_host_attribute_list",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/add/$",
        views.hosts.HostOwnerAdd.as_view(),
        name="api_host_owners_delete",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/delete/$",
        views.hosts.HostOwnerDelete.as_view(),
        name="api_host_owners_add",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/$",
        views.hosts.HostOwnerList.as_view(),
        name="api_host_owners_list",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/renew/$",
        views.hosts.HostRenew.as_view(),
        name="api_host_renew",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/update/$",
        views.hosts.HostUpdate.as_view(),
        name="api_host_update",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$",
        views.hosts.HostDelete.as_view(),
        name="api_host_delete",
    ),
    url(
        r"^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/$",
        views.hosts.HostDetail.as_view(),
        name="api_host_view",
    ),
    url(r"^hosts/add/$", views.hosts.HostCreate.as_view(), name="api_host_add"),
    url(
        r"^hosts/disabled/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$",
        views.hosts.DisabledHostDelete.as_view(),
        name="api_disabled_hosts_delete",
    ),
    url(
        r"^hosts/disabled/add/$",
        views.hosts.DisabledHostCreate.as_view(),
        name="api_disabled_hosts_add",
    ),
    url(
        r"^hosts/disabled/$",
        views.hosts.DisabledHostList.as_view(),
        name="api_disabled_hosts_list",
    ),
    url(r"^hosts/$", views.hosts.HostList.as_view(), name="api_host_list"),
    url(
        r"^guests/register/$",
        views.guests.GuestRegister.as_view(),
        name="api_guest_register",
    ),
    url(
        r"^guests/tickets/add/$",
        views.guests.GuestTicketCreate.as_view(),
        name="api_guest_create",
    ),
    url(
        r"^guests/tickets/$",
        views.guests.GuestTicketList.as_view(),
        name="api_guest_list",
    ),
    url(
        r"^guests/tickets/(?P<ticket>\w+)/$",
        views.guests.GuestTicketDelete.as_view(),
        name="api_guest_delete",
    ),
    url(
        r"^dns/(?P<pk>\d+)/delete/$",
        views.dns.DnsDelete.as_view(),
        name="api_dns_delete",
    ),
    url(r"^dns/(?P<pk>\d+)/$", views.dns.DnsDetail.as_view(), name="api_dns_view"),
    url(r"^dns/add/$", views.dns.DnsCreate.as_view(), name="api_dns_add"),
    url(r"^dns/$", views.dns.DnsList.as_view(), name="api_dns_list"),
    url(r"^domain/$", views.dns.DomainList.as_view(), name="api_domain_list"),
    url(
        r"^domain/name/$",
        views.dns.DomainNameList.as_view(),
        name="api_domain_name_list",
    ),
    url(r"^network/$", views.network.NetworkList.as_view(), name="api_network_list"),
    url(
        r"^network/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,2}))/$",
        views.network.NetworkDetail.as_view(),
        name="api_network_detail",
    ),
    url(
        r"^network/add/$",
        views.network.NetworkCreate.as_view(),
        name="api_network_create",
    ),
    url(
        r"^network/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,3}))/update/$",
        views.network.NetworkUpdate.as_view(),
        name="api_network_update",
    ),
    url(
        r"^network/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,3}))/delete/$",
        views.network.NetworkDelete.as_view(),
        name="api_network_delete",
    ),
    url(
        r"^address/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/$",
        views.network.AddressDetail.as_view(),
        name="api_address_view",
    ),
    url(
        r"^address/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/update/$",
        views.network.AddressUpdate.as_view(),
        name="api_address_update",
    ),
    url(r"^address/$", views.network.AddressList.as_view(), name="api_address_list"),
    url(
        r"^login/has_auth/", views.base.UserAuthenticated.as_view(), name="api_has_auth"
    ),
    url(r"^login/jwt_token/", views.base.obtain_jwt_token),
    url(
        r"^docs",
        schema_view.with_ui("swagger", cache_timeout=None),
        name="schema-swagger",
    ),
    url(r"^", include("rest_framework.urls", namespace="rest_framework")),
]
