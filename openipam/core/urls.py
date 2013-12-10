from django.conf.urls import patterns, url, include
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete, password_change, password_change_done
from django.views.generic import TemplateView
from openipam.core.views import FeatureRequestView


urlpatterns = patterns('openipam.core.views',
    url(r'^$', 'index', name='index'),

    # Accounts URLs
    #url(r'^accounts/login/$', login, name='auth_login'),
    #url(r'^accounts/password/reset/$', password_reset),
    #url(r'^accounts/logout/$', logout, name='auth_logout'),
    #url(r'^accounts/profile/$', 'profile', name='profile'),

    # Hosts
    url(r'^api/', include('openipam.api.urls')),

    # Hosts
    url(r'^hosts/', include('openipam.hosts.urls')),

    # DNS
    url(r'^dns/', include('openipam.dns.urls')),

    # Account URLS
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^password/forgot/$', 'password_forgot', name='password_forgot'),
    url(r'^password/change/$', 'password_change', name='password_change'),
    url(r'^password/change/done/$', password_change_done, name='password_change_done'),
    url(r'^password/reset/$', password_reset, name='password_reset'),
    url(r'^password/reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', password_reset_complete, name='password_reset_complete'),
    url(r'^request/complete/$',
       TemplateView.as_view(template_name='core/featurerequest_form.html'),
       {'is_complete': True},
       name='feature_request_complete'),
    url(r'^request/$', FeatureRequestView.as_view(), name='feature_request'),
)
