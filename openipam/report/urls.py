from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView


urlpatterns = patterns('openipam.report.views',

    url(r'^leases/usage/$', 'lease_usage', name='reports_lease_usage'),
    url(r'^leases/available/$', 'leases_available', name='reports_leases_available'),
    url(r'^weathermap/$', 'weather_map', name='reports_weather_map'),
    url(r'^$', 'overview', name='reports_dashboard'),
)
