from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from openipam.user.views import UserManagerJson, UserManagerView

urlpatterns = patterns('openipam.user.views',
    url(r'^user/$', RedirectView.as_view(pattern_name='user_manager'), name='user_manager_redirect'),
    url(r'^manager/$', UserManagerView.as_view(), name='user_manager'),
    url(r'^manager/user/(?P<pk>\d+)$', 'user_detail', name='user_detail'),
    url(r'^manager/data/$', UserManagerJson.as_view(), name='json_hosts'),
    url(r'^manager/groups/(?P<pk>\d+)$', 'user_groups', name='user_groups'),
    url(r'^manager/permissions/(?P<pk>\d+)$', 'user_permissions', name='user_permissions'),
)
