# from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.views.generic.edit import CreateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.admin.sites import AdminSite
from django.views.decorators.csrf import requires_csrf_token
from django.template import loader
from django.conf import settings
from django.utils.encoding import force_text
from django.contrib.auth import get_user_model

# from django.contrib.auth.views import (
#     login as auth_login_view,
#     logout as auth_logout_view,
# )
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.utils.translation import ugettext as _
from django.utils.cache import add_never_cache_headers
from django.views.generic.base import TemplateView
from django.db.utils import DataError
from django.urls import reverse

from openipam.core.models import FeatureRequest
from openipam.core.forms import ProfileForm, FeatureRequestForm

# from openipam.user.forms import IPAMAuthenticationForm
from openipam.conf.ipam_settings import CONFIG

import duo_web

import os
import random
import sys
import json

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def index(request):
    if CONFIG.get("DUO_LOGIN") and not is_duo_authenticated(request):
        return redirect("core:duo_auth")
    if not request.user.get_full_name() or not request.user.email:
        return redirect("core:profile")
    else:
        context = {
            "email": CONFIG.get("EMAIL_ADDRESS"),
            "legacy_domain": CONFIG.get("LEGACY_DOAMIN"),
        }
        return AdminSite().index(request, extra_context=context)


def mimic(request):
    if request.POST and request.user.is_ipamadmin:
        mimic_pk = request.POST.get("mimic_pk")
        if mimic_pk:
            try:
                mimic_user = User.objects.get(pk=mimic_pk)
            except User.DoesNotExist:
                return redirect("core:index")
            request.session["mimic_user"] = mimic_user.pk
    else:
        if "mimic_user" in request.session:
            del request.session["mimic_user"]

    return redirect("core:index")


def profile(request):
    """Profile view used with accounts"""

    form = ProfileForm(request.POST or None, instance=request.user)

    groups = request.user.groups.all()

    # if len(form.initial) < 3:
    #     profile_complete = False
    # else:
    #     for key in form.initial:
    #         if not form.initial[key]:
    #             profile_complete = False
    #             break
    #         else:
    #             profile_complete = True

    if form.is_valid():
        form.save()

        messages.add_message(request, messages.INFO, "Your profile has been updated.")
        return redirect("core:profile")

    context = {
        "title": "Profile for %s" % request.user.get_full_name(),
        "groups": groups,
        "form": form,
    }

    return render(request, "registration/profile.html", context)


def duo_auth(request):
    if is_duo_authenticated(request):
        return redirect("core:index")

    sig_request = None
    duo_settings = CONFIG.get("DUO_SETTINGS", {})

    if request.POST:
        sig_response = request.POST.get("sig_response", None)
        if sig_response:
            authenticated_username = duo_web.verify_response(
                duo_settings.get("IKEY"),
                duo_settings.get("SKEY"),
                duo_settings.get("AKEY"),
                sig_response,
            )
            if authenticated_username:
                duo_authenticate(request)
                redirect_val = request.GET.get("next", "admin:index")
                if redirect_val is None:
                    return redirect("admin:index")
                return redirect(redirect_val)

    sig_request = duo_web.sign_request(
        duo_settings.get("IKEY"),
        duo_settings.get("SKEY"),
        duo_settings.get("AKEY"),
        request.user.username,
    )

    context = {
        "sig_request": sig_request,
        "host": duo_settings.get("HOST"),
        "post_action": f"{reverse('duo_auth')}?next={request.GET.get('next')}",
    }
    return render(request, "registration/duo.html", context)


def is_duo_authenticated(request):
    return request.session.get("duo_authenticated", False)


def duo_authenticate(request):
    request.session["duo_authenticated"] = request.user.username


class IPAMPasswordChangeView(PasswordChangeView):
    def get_form_kwargs(self):
        if self.request.user.has_usable_password():
            return super().get_form_kwargs()
        else:
            return redirect("admin:index")


@requires_csrf_token
def bad_request(request, exception):
    return page_error(request, exception=exception, template_name="400.html")


@requires_csrf_token
def page_denied(request, exception):
    return page_error(request, exception=exception, template_name="403.html")


@requires_csrf_token
def page_not_found(request, exception):
    return page_error(request, exception=exception, template_name="404.html")


@requires_csrf_token
def server_error(request):
    return page_error(request, template_name="500.html")


def page_error(request, template_name, exception=None, extra_context=None):
    kitty_dir = (
        os.path.dirname(os.path.realpath(__file__)) + "/static/core/img/error_cats"
    )
    kitty = random.choice(os.listdir(kitty_dir))
    template = loader.get_template(template_name)
    error_type, error_value, traceback = sys.exc_info()
    context = {
        "request": request,
        "request_path": request.path,
        "kitty": kitty,
        "email": CONFIG.get("EMAIL_ADDRESS"),
        "error_type": error_type.__name__,
        "error_value": error_value,
        "traceback": traceback,
        "exception": exception,
    }
    if extra_context:
        context.update(extra_context)
    body = template.render(context, request)
    return HttpResponseNotFound(body, content_type="text/html")


class FeatureRequestView(CreateView):
    form_class = FeatureRequestForm
    model = FeatureRequest
    success_url = reverse_lazy("core:feature_request_complete")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.is_complete = False
        self.object.save()
        if self.request.is_ajax():
            return HttpResponse(1)
        else:
            return HttpResponseRedirect(self.get_success_url())


class LazyEncoder(DjangoJSONEncoder):
    """Encodes django's lazy i18n strings"""

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONResponseMixin(object):
    is_clean = False

    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(context)

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        response = HttpResponse(
            content, content_type="application/json", **httpresponse_kwargs
        )
        add_never_cache_headers(response)
        return response

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.request = request
        data = request.GET.get("json_data")
        if data:
            self.json_data = json.loads(data)
        else:
            return self.render_to_response("")

        response = None

        try:
            func_val = self.get_context_data(**kwargs)
            if not self.is_clean:
                assert isinstance(func_val, dict)
                response = dict(func_val)
                if "result" not in response:
                    response["result"] = "ok"
            else:
                response = func_val
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception as e:
            # Just re raise if we are DEBUG
            if settings.DEBUG:
                raise

            logger.error("JSON view error: %s" % request.path, exc_info=True)
            exc_type, exc_obj, exc_tb = sys.exc_info()

            # Come what may, we're returning JSON.
            if hasattr(e, "message"):
                msg = "%s: " % exc_type.__name__
                msg += str(e.message)
            else:
                msg = _("Internal error") + ": " + str(e)

            response = {"result": "error", "text": msg}

        dump = json.dumps(response, cls=LazyEncoder)
        return self.render_to_response(dump)


class BaseDatatableView(JSONResponseMixin, TemplateView):
    """JSON data for datatables"""

    model = None
    columns = []
    order_columns = []
    max_display_length = 100  # max limit of records returned, do not allow to kill our server by huge sets of data

    def initialize(*args, **kwargs):
        pass

    def get_order_columns(self):
        """Return list of columns used for ordering"""
        return self.order_columns

    def get_columns(self):
        """Returns the list of columns that are returned in the result set"""
        return self.columns

    def render_column(self, row, column):
        """Renders a column on a row"""
        if hasattr(row, "get_%s_display" % column):
            # It's a choice field
            text = getattr(row, "get_%s_display" % column)()
        else:
            try:
                text = getattr(row, column)
            except AttributeError:
                obj = row
                for part in column.split("."):
                    if obj is None:
                        break
                    obj = getattr(obj, part)

                text = obj

        if hasattr(row, "get_absolute_url"):
            return '<a href="%s">%s</a>' % (row.get_absolute_url(), text)
        else:
            return text

    def ordering(self, qs):
        """Get parameters from the request and prepare order by clause"""
        # Number of columns that are used in sorting
        order_data = self.json_data.get("order", [])

        order = []
        order_columns = self.get_order_columns()
        for item in order_data:
            column = item["column"]
            column_dir = item["dir"]
            sdir = "-" if column_dir == "desc" else ""
            sortcol = order_columns[column]
            order.append("%s%s" % (sdir, sortcol))

        if order:
            return qs.order_by(*order)
        return qs

    def paging(self, qs):
        """Paging"""
        limit = min(int(self.json_data.get("length", 10)), self.max_display_length)
        # if pagination is disabled ("bPaginate": false)
        if limit == -1:
            return qs
        start = int(self.json_data.get("start", 0))
        offset = start + limit
        return qs[start:offset]

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError(
                "Need to provide a model or implement get_initial_queryset!"
            )
        return self.model.objects.all()

    def filter_queryset(self, qs):
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append(
                [self.render_column(item, column) for column in self.get_columns()]
            )
        return data

    def get_context_data(self, *args, **kwargs):
        try:
            self.initialize(*args, **kwargs)

            qs = self.get_initial_queryset()

            # number of records before filtering
            records_total = qs.count()

            qs = self.filter_queryset(qs)

            # number of records after filtering
            records_filtered = qs.count()

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # prepare output data
            data = self.prepare_results(qs)

            ret = {
                "draw": int(self.json_data.get("draw", 0)),
                "recordsTotal": records_total,
                "recordsFiltered": records_filtered,
                "data": data,
            }
        except (ValidationError, DataError):
            ret = {
                "draw": int(self.json_data.get("draw", 0)),
                "recordsTotal": records_total,
                "recordsFiltered": 0,
                "data": [],
            }

        return ret
