from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import REDIRECT_FIELD_NAME

from re import compile

User = get_user_model()


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware(object):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """

    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."
        if not request.user.is_authenticated():
            path = request.path.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL + '?%s=%s' % (REDIRECT_FIELD_NAME, request.path))


class MimicUserMiddleware(object):
    def process_request(self, request):
        mimic_user = request.session.get('mimic_user')
        if mimic_user:
            try:
                request.user = User.objects.get(pk=mimic_user)
            except User.DoesNotExist:
                del request.session['mimic_user']
