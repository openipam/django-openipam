from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from openipam.conf.ipam_settings import CONFIG

from re import compile

User = get_user_model()


EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip("/"))]
if hasattr(settings, "LOGIN_EXEMPT_URLS"):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class SetRemoteAddrMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META.get("REMOTE_ADDR") == "127.0.0.1":
            try:
                request.META["OLD_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
                request.META["REMOTE_ADDR"] = request.META["HTTP_X_REAL_IP"]
            except Exception:
                pass


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, "user")
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/")
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL)


class DuoAuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(
            request, "user"
        ), "The Duo Auth Required middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."

        duo_exempt_urls = [
            reverse("core:profile"),
            reverse("core:password_change"),
            reverse("core:password_change_done"),
            reverse("core:duo_auth"),
        ]

        if CONFIG.get("DUO_LOGIN"):
            if request.user.is_authenticated() and not request.session.get(
                "duo_authenticated", False
            ):
                path = request.path.lstrip("/")
                if not any(m.match(path) for m in EXEMPT_URLS):
                    if request.path not in duo_exempt_urls:
                        return redirect(f"{reverse('duo_auth')}?next={request.path}")


class MimicUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        mimic_user = request.session.get("mimic_user")
        if mimic_user:
            try:
                request.user = User.objects.get(pk=mimic_user)
            except User.DoesNotExist:
                del request.session["mimic_user"]
