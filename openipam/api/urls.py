from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt

from rest_framework.routers import SimpleRouter, Route

from openipam.api import views

app_name = "api"


class OPENIPAMAPIRouter(SimpleRouter):
    """
    A router to match existing url patterns
    """

    routes = [
        Route(
            url="{prefix}/",
            mapping={"get": "list"},
            name="api_{basename}_list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        Route(
            url="{prefix}/add/",
            mapping={"post": "create"},
            name="api_{basename}_create",
            detail=False,
            initkwargs={"suffix": "Create"},
        ),
        Route(
            url="{prefix}/{lookup}/",
            mapping={"get": "retrieve"},
            name="api_{basename}_detail",
            detail=True,
            initkwargs={"suffix": "Detail"},
        ),
        Route(
            url="{prefix}/{lookup}/update/",
            mapping={"get": "retrieve", "post": "update", "put": "update"},
            name="api_{basename}_update",
            detail=True,
            initkwargs={"suffix": "Update"},
        ),
        Route(
            url="{prefix}/{lookup}/delete/",
            mapping={"get": "retrieve", "delete": "destroy", "post": "destroy"},
            name="api_{basename}_delete",
            detail=True,
            initkwargs={"suffix": "Delete"},
        ),
    ]


router = OPENIPAMAPIRouter()
router.register(r"dhcpgroups?", views.network.DhcpGroupViewSet)
router.register(r"dhcpoptions?", views.network.DhcpOptionViewSet)
router.register(r"dhcpoptiontodhcpgroups?", views.network.DhcpOptionToDhcpGroupViewSet)
router.register(r"sharednetworks?", views.network.SharedNetworkViewSet)
router.register(r"networkranges?", views.network.NetworkRangeViewSet)
router.register(r"networks?tovlans?", views.network.NetworkToVlanViewSet)
router.register(r"pools?", views.network.PoolViewSet)
router.register(r"defaultpools?", views.network.DefaultPoolViewSet)
router.register(r"vlans?", views.network.VlanViewSet)
router.register(r"buildings?", views.network.BuildingViewSet)
router.register(r"buildings?tovlans?", views.network.BuildingToVlanViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "network/router_upgrade/",
        csrf_exempt(views.network.RouterUpgrade.as_view()),
        name="router_upgrade",
    ),
    path("web/show_users/<int:group_id>/", views.web.show_users, name="api_show_users"),
    path(
        "web/networkselects/<int:address_type_id>/",
        views.web.network_selects,
        name="api_network_select",
    ),
    path(
        "web/structuredattributevalues/<int:attribute_id>",
        views.web.structured_attribute_selects,
        name="api_structured_attribute_select",
    ),
    # Reports
    path(
        "reports/serverhosts/",
        views.report.ServerHostView.as_view(),
        name="api_reports_server_hosts",
    ),
    path(
        "reports/leaseusage/",
        views.report.LeaseUsageView.as_view(),
        name="api_reports_lease_usage",
    ),
    re_path(
        r"^reports/leasegraph/(?P<network>.*)/$",
        views.report.LeaseGraphView.as_view(),
        name="api_reports_lease_graph",
    ),
    path(
        "reports/weathermap/",
        views.report.WeatherMapView.as_view(),
        name="api_reports_weather_map",
    ),
    path(
        "reports/weathermap/config.json",
        views.report.weathermap_config,
        name="api_reports_weather_map_config",
    ),
    path(
        "reports/buildingmap/config.json",
        views.report.buildingmap_config,
        name="api_reports_buildingmap_config",
    ),
    path(
        "reports/chartstats/",
        views.report.StatsAPIView.as_view(),
        name="api_reports_chart_stats",
    ),
    path(
        "reports/dashboard/",
        views.report.DashboardAPIView.as_view(),
        name="api_reports_dashboard",
    ),
    # Users
    re_path(r"^users?/$", views.users.UserList.as_view(), name="api_users_list"),
    # Groups
    re_path(r"^groups?/$", views.users.GroupList.as_view(), name="api_groups_list"),
    re_path(
        r"^groups?/options/$",
        views.users.GroupOptionsList.as_view(),
        name="api_groupsoptions_list",
    ),
    # Attributes
    re_path(
        r"^attributes?/$", views.hosts.AttributeList.as_view(), name="api_attributes"
    ),
    re_path(
        r"^attributes?/structured/values/$",
        views.hosts.StructuredAttributeValueList.as_view(),
        name="api_attributes_structured_values",
    ),
    # Hosts
    re_path(
        r"^hosts?/mac/next/$",
        views.hosts.HostNextMac.as_view(),
        name="api_host_mac_next",
    ),
    re_path(r"^hosts?/mac/$", views.hosts.HostMac.as_view(), name="api_host_mac"),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/add/$",
        views.hosts.HostAddAttribute.as_view(),
        name="api_host_attribute_add",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/delete/$",
        views.hosts.HostDeleteAttribute.as_view(),
        name="api_host_attribute_delete",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/$",
        views.hosts.HostAttributeList.as_view(),
        name="api_host_attribute_list",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/add/$",
        views.hosts.HostOwnerAdd.as_view(),
        name="api_host_owners_delete",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/delete/$",
        views.hosts.HostOwnerDelete.as_view(),
        name="api_host_owners_add",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/$",
        views.hosts.HostOwnerList.as_view(),
        name="api_host_owners_list",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/renew/$",
        views.hosts.HostRenew.as_view(),
        name="api_host_renew",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/update/$",
        views.hosts.HostUpdate.as_view(),
        name="api_host_update",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$",
        views.hosts.HostDelete.as_view(),
        name="api_host_delete",
    ),
    re_path(
        r"^hosts?/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/$",
        views.hosts.HostDetail.as_view(),
        name="api_host_view",
    ),
    re_path(r"^hosts?/add/$", views.hosts.HostCreate.as_view(), name="api_host_add"),
    re_path(
        r"^hosts?/disabled/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$",
        views.hosts.DisabledHostDelete.as_view(),
        name="api_disabled_hosts_delete",
    ),
    re_path(
        r"^hosts?/disabled/add/$",
        views.hosts.DisabledHostCreate.as_view(),
        name="api_disabled_hosts_add",
    ),
    re_path(
        r"^hosts?/disabled/$",
        views.hosts.DisabledHostList.as_view(),
        name="api_disabled_hosts_list",
    ),
    re_path(r"^hosts?/$", views.hosts.HostList.as_view(), name="api_host_list"),
    re_path(
        r"^guests?/register/$",
        views.guests.GuestRegister.as_view(),
        name="api_guest_register",
    ),
    re_path(
        r"^guests?/tickets/add/$",
        views.guests.GuestTicketCreate.as_view(),
        name="api_guest_create",
    ),
    re_path(
        r"^guests?/tickets/$",
        views.guests.GuestTicketList.as_view(),
        name="api_guest_list",
    ),
    re_path(
        r"^guests?/tickets/(?P<ticket>\w+)/$",
        views.guests.GuestTicketDelete.as_view(),
        name="api_guest_delete",
    ),
    path("dns/<int:pk>/delete/", views.dns.DnsDelete.as_view(), name="api_dns_delete"),
    path("dns/<int:pk>/", views.dns.DnsDetail.as_view(), name="api_dns_view"),
    path("dns/add/", views.dns.DnsCreate.as_view(), name="api_dns_add"),
    path("dns/", views.dns.DnsList.as_view(), name="api_dns_list"),
    re_path(r"^domains?/$", views.dns.DomainList.as_view(), name="api_domain_list"),
    re_path(
        r"^domains?/name/$",
        views.dns.DomainNameList.as_view(),
        name="api_domain_name_list",
    ),
    re_path(
        r"^networks?/$", views.network.NetworkList.as_view(), name="api_network_list"
    ),
    re_path(
        r"^networks?/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,2}))/$",
        views.network.NetworkDetail.as_view(),
        name="api_network_detail",
    ),
    re_path(
        r"^networks?/add/$",
        views.network.NetworkCreate.as_view(),
        name="api_network_create",
    ),
    re_path(
        r"^networks?/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,3}))/update/$",
        views.network.NetworkUpdate.as_view(),
        name="api_network_update",
    ),
    re_path(
        r"^networks?/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}\/\d{0,3}))/delete/$",
        views.network.NetworkDelete.as_view(),
        name="api_network_delete",
    ),
    re_path(
        r"^address(es)?/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/$",
        views.network.AddressDetail.as_view(),
        name="api_address_view",
    ),
    re_path(
        r"^address(es)?/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/update/$",
        views.network.AddressUpdate.as_view(),
        name="api_address_update",
    ),
    re_path(
        r"^address(es)?/$", views.network.AddressList.as_view(), name="api_address_list"
    ),
    path(
        "base/overview/",
        views.base.OverviewStatsAPI.as_view(),
        name="api_overview_stats",
    ),
    path(
        "login/has_auth/", views.base.UserAuthenticated.as_view(), name="api_has_auth"
    ),
    path("login/jwt_token/", views.base.obtain_jwt_token),
    path("", include("rest_framework.urls", namespace="rest_framework")),
]
