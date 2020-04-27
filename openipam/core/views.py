# from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.views.generic.edit import CreateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.admin.sites import AdminSite
from django.views.decorators.csrf import requires_csrf_token, csrf_exempt
from django.template import loader
from django.conf import settings
from django.utils.encoding import force_text
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.aggregates import Count
from django.db.models import Q

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

# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.utils import timezone

from openipam.core.models import FeatureRequest, Bookmark
from openipam.core.forms import ProfileForm, FeatureRequestForm

# from openipam.user.forms import IPAMAuthenticationForm
from openipam.conf.ipam_settings import CONFIG
from openipam.dns.models import DnsRecord
from openipam.hosts.models import Host
from openipam.log.models import LeaseLog, EmailLog, UserLog
from openipam.network.models import Lease, Network, Address
from openipam.core.forms import ProfileForm, FeatureRequestForm, BookmarkForm

# from openipam.user.forms import IPAMAuthenticationForm

import qsstats
from chartjs.views.lines import BaseLineChartView
from chartjs.colors import next_color
import duo_web
from functools import reduce
import os
import random
import sys
import json
import datetime
import operator
import logging

# from django_cas_ng.views import login as cas_login, logout as cas_logout
# from django_cas_ng.utils import get_cas_client, get_protocol, get_redirect_url


logger = logging.getLogger(__name__)

User = get_user_model()


COLORS = [
    (202, 201, 197),  # Light gray
    # (171, 9, 0),      # Red
    (166, 78, 46),  # Light orange
    # (255, 190, 67),  # Yellow
    # (163, 191, 63),   # Light green
    (122, 159, 191),  # Light blue
    # (140, 5, 84),  # Pink
    (166, 133, 93),  # Light brown
    # (75, 64, 191),  # Red blue
    # (237, 124, 60),  # orange
]


class DashbardStatsJSONView(BaseLineChartView):
    def get_colors(self):
        return next_color(color_list=COLORS)

    def get_labels(self):
        """Return 7 labels for the x-axis."""
        today = datetime.date.today()
        td = datetime.timedelta
        return [
            today + td(-6),
            today + td(-5),
            today + td(-4),
            today + td(-3),
            today + td(-2),
            today + td(-1),
            today,
        ]

    def get_providers(self):
        """Return names of datasets."""
        return ["Wireless Leases", "Total Leases", "Active Users", "Notifications Sent"]

    def get_data(self):
        """Return 3 datasets to plot."""

        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        wireless_networks_available_qs = [
            Q(address__address__net_contained=network.network)
            for network in wireless_networks
        ]
        user_qs = UserLog.objects.filter(trigger_tuple="new")
        lease_sq = LeaseLog.objects.filter(trigger_tuple="new")
        # dns_qs = DnsRecordLog.objects.filter(trigger_tuple="new")
        notify_qs = EmailLog.objects.filter(subject__icontains="[USU:Important]")
        wireless_qs = LeaseLog.objects.filter(
            reduce(operator.or_, wireless_networks_available_qs)
        )

        user_stats = qsstats.QuerySetStats(user_qs, "last_login", aggregate=Count("pk"))
        lease_stats = qsstats.QuerySetStats(lease_sq, "starts", aggregate=Count("pk"))
        # dns_stats = qsstats.QuerySetStats(dns_qs, "changed", aggregate=Count("pk"))
        notify_stats = qsstats.QuerySetStats(notify_qs, "when", aggregate=Count("pk"))
        wireless_stats = qsstats.QuerySetStats(
            wireless_qs, "starts", aggregate=Count("pk")
        )

        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)

        user_time_series = user_stats.time_series(seven_days_ago, today)
        lease_time_series = lease_stats.time_series(seven_days_ago, today)
        # dns_time_series = dns_stats.time_series(seven_days_ago, today)
        notify_time_series = notify_stats.time_series(seven_days_ago, today)
        wireless_time_series = wireless_stats.time_series(seven_days_ago, today)

        return [
            [n for t, n in wireless_time_series],
            [n for t, n in lease_time_series],
            [n for t, n in user_time_series],
            [n for t, n in notify_time_series],
        ]


def index(request):
    if CONFIG.get("DUO_LOGIN") and not is_duo_authenticated(request):
        return redirect("duo_auth")
    if not request.user.get_full_name() or not request.user.email:
        return redirect("core:profile")
    else:
        context = {
            "email": CONFIG.get("EMAIL_ADDRESS"),
            "legacy_domain": CONFIG.get("LEGACY_DOAMIN"),
        }

        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        wireless_networks_available_qs = [
            Q(address__net_contained=network.network) for network in wireless_networks
        ]

        context.update(
            {
                "dynamic_hosts": Host.objects.filter(
                    pools__isnull=False, expires__gte=timezone.now()
                ).count(),
                "static_hosts": Host.objects.filter(
                    addresses__isnull=False, expires__gte=timezone.now()
                ).count(),
                "active_leases": Lease.objects.filter(ends__gte=timezone.now()).count(),
                "abandoned_leases": Lease.objects.filter(abandoned=True).count(),
                "total_networks": Network.objects.all().count(),
                "wireless_networks": wireless_networks.count(),
                "wireless_addresses_total": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs)
                ).count(),
                "wireless_addresses_available": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs),
                    leases__ends__lt=timezone.now(),
                ).count(),
                "dns_a_records": DnsRecord.objects.filter(
                    dns_type__name__in=["A", "AAAA"]
                ).count(),
                "dns_cname_records": DnsRecord.objects.filter(
                    dns_type__name="CNAME"
                ).count(),
                "dns_mx_records": DnsRecord.objects.filter(dns_type__name="MX").count(),
                "active_users": User.objects.filter(
                    last_login__gte=(timezone.now() - datetime.timedelta(days=365))
                ).count(),
            }
        )

        return AdminSite().index(request, extra_context=context)


# @csrf_exempt
# @require_http_methods(["GET", "POST"])
# def login(request, internal=False, **kwargs):
#     # if CONFIG.get("CAS_LOGIN") and internal is False:
#     #     return cas_login(request, **kwargs)
#     # else:
#     return auth_login_view(
#         request, authentication_form=IPAMAuthenticationForm, **kwargs
#     )


# @require_http_methods(["GET"])
# def logout(request, next_page=None, **kwargs):


# backend = request.session.get("_auth_user_backend", "").split(".")[-1]

# if CONFIG.get("CAS_LOGIN") and backend == "IPAMCASBackend":
#     cas_logout(request, next_page, **kwargs)

#     next_page = next_page or get_redirect_url(request)
#     if settings.CAS_LOGOUT_COMPLETELY:
#         protocol = get_protocol(request)
#         host = request.get_host()
#         redirect_url = urllib_parse.urlunparse(
#             (protocol, host, next_page, "", "", "")
#         )
#         client = get_cas_client()
#         client.server_url = settings.CAS_SERVER_URL[:-3]
#         return HttpResponseRedirect(client.get_logout_url(redirect_url))
#     else:
#         # This is in most cases pointless if not CAS_RENEW is set. The user will
#         # simply be logged in again on next request requiring authorization.
#         return HttpResponseRedirect(next_page)
# else:
# next_page = "internal_login" if CONFIG.get("CAS_LOGIN") else "login"
# return auth_logout_view(request, next_page="login", **kwargs)


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


@staff_member_required
@csrf_exempt
def add_bookmark(request):
    """
    This view serves and validates a bookmark form.
    If requested via ajax it also returns the drop bookmark form to replace the
    add bookmark form.
    """
    if request.method == "POST":
        form = BookmarkForm(user=request.user, data=request.POST)
        if form.is_valid():
            bookmark = form.save()
            if not request.is_ajax():
                messages.success(request, "Bookmark added")
                if request.POST.get("next"):
                    return HttpResponseRedirect(request.POST.get("next"))
                return HttpResponse("Added")
            return render(
                request,
                "core/menu/remove_bookmark_form.html",
                context={"bookmark": bookmark, "url": bookmark.url},
            )
    else:
        form = BookmarkForm(user=request.user)
    return render(
        request, "core/menu/form.html", context={"form": form, "title": "Add Bookmark"}
    )


@staff_member_required
@csrf_exempt
def edit_bookmark(request, id):
    bookmark = get_object_or_404(Bookmark, id=id)
    if request.method == "POST":
        form = BookmarkForm(user=request.user, data=request.POST, instance=bookmark)
        if form.is_valid():
            form.save()
            if not request.is_ajax():
                messages.success(request, "Bookmark updated")
                if request.POST.get("next"):
                    return HttpResponseRedirect(request.POST.get("next"))
            return HttpResponse("Saved")
    else:
        form = BookmarkForm(user=request.user, instance=bookmark)
    return render(
        request, "core/menu/form.html", context={"form": form, "title": "Edit Bookmark"}
    )


@staff_member_required
@csrf_exempt
def remove_bookmark(request, id):
    """
    This view deletes a bookmark.
    If requested via ajax it also returns the add bookmark form to replace the
    drop bookmark form.
    """
    bookmark = get_object_or_404(Bookmark, id=id, user=request.user)
    if request.method == "POST":
        bookmark.delete()
        if not request.is_ajax():
            messages.success(request, "Bookmark removed")
            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST.get("next"))
            return HttpResponse("Deleted")
        return render(
            request,
            "admin_tools/menu/add_bookmark_form.html",
            context={
                "url": request.POST.get("next"),
                "title": "**title**",  # replaced on the javascript side
            },
        )
    return render(
        request,
        "admin_tools/menu/delete_confirm.html",
        context={"bookmark": bookmark, "title": "Delete Bookmark"},
    )


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

    if request.user.get_full_name():
        name = request.user.get_full_name()

    else:
        name = request.user.username

    context = {
        "title": "Profile for %s" % name,
        "groups": groups,
        "form": form,
    }

    return render(request, "registration/profile.html", context)


def duo_auth(request):
    if is_duo_authenticated(request):
        return redirect("index")

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
                return redirect(request.GET.get("next", "admin:index"))

    sig_request = duo_web.sign_request(
        duo_settings.get("IKEY"),
        duo_settings.get("SKEY"),
        duo_settings.get("AKEY"),
        request.user.username,
    )

    context = {
        "sig_request": sig_request,
        "host": duo_settings.get("HOST"),
        "post_action": f"{reverse('core:duo_auth')}?next={request.GET.get('next')}",
    }
    return render(request, "registration/duo.html", context)


def is_duo_authenticated(request):
    return request.session.get("duo_authenticated", False)


def duo_authenticate(request):
    request.session["duo_authenticated"] = request.user.username


# def password_change(request, *args, **kwargs):
#     if request.user.has_usable_password():
#         return PasswordChangeView(request, *args, **kwargs)
#     else:
#         return redirect("admin:index")


class IPAMPasswordChangeView(PasswordChangeView):
    def get_form_kwargs(self):
        if self.request.user.has_usable_password():
            return super(self, IPAMPasswordChangeView).get_form_kwargs(self)
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
    """Encodes django's lazy i18n strings
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONResponseMixin(object):
    is_clean = False

    def render_to_response(self, context):
        """ Returns a JSON response containing 'context' as payload
        """
        return self.get_json_response(context)

    def get_json_response(self, content, **httpresponse_kwargs):
        """ Construct an `HttpResponse` object.
        """
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
    """ JSON data for datatables
    """

    model = None
    columns = []
    order_columns = []
    max_display_length = 100

    def initialize(*args, **kwargs):
        pass

    def get_order_columns(self):
        """ Return list of columns used for ordering
        """
        return self.order_columns

    def get_columns(self):
        """ Returns the list of columns that are returned in the result set
        """
        return self.columns

    def render_column(self, row, column):
        """ Renders a column on a row
        """
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
        """ Get parameters from the request and prepare order by clause
        """
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
        """ Paging
        """
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
