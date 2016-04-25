from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView

from openipam.report.views import DashboardView, LeaseUsageView, WeatherMapView, DisabledHostsView, ServerHostsView


urlpatterns = patterns('openipam.report.views',
    url(r'^leases/usage/$', LeaseUsageView.as_view(), name='reports_lease_usage'),
    url(r'^weathermap/$', WeatherMapView.as_view(), name='reports_weather_map'),
    url(r'^disabled/$', DisabledHostsView.as_view(), name='reports_disabled'),
    url(r'^server_hosts/$', ServerHostsView.as_view(), name='reports_server_hosts'),
    url(r'^$', DashboardView.as_view(), name='reports_dashboard'),
)
