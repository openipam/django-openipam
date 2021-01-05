from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView, View
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.http import urlunquote
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.db.utils import DatabaseError
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.core import serializers
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorList, ErrorDict

from openipam.core.views import BaseDatatableView
from openipam.hosts.decorators import permission_change_host
from openipam.hosts.forms import (
    HostForm,
    HostOwnerForm,
    HostRenewForm,
    HostBulkCreateForm,
    HostAttributesDeleteForm,
    HostRenameForm,
    HostDhcpGroupForm,
    HostNetworkForm,
)
from openipam.hosts.models import Host, Disabled, Attribute, FreeformAttributeToHost
from openipam.network.models import Address, AddressType
from openipam.hosts.actions import (
    delete_hosts,
    renew_hosts,
    assign_owner_hosts,
    remove_owner_hosts,
    add_attribute_to_hosts,
    delete_attribute_from_host,
    populate_primary_dns,
    export_csv,
    rename_hosts,
    set_dhcp_group_on_host,
    delete_dhcp_group_on_host,
    change_network_on_host,
)
from openipam.conf.ipam_settings import CONFIG

from braces.views import PermissionRequiredMixin, SuperuserRequiredMixin

from itertools import zip_longest

import json
import re
import csv
import collections

User = get_user_model()


class HostListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = "hosts.view_host"

    order_columns = ("pk", "hostname", "mac", "expires", "addresses")

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 3000

    def get_initial_queryset(self):
        qs = Host.objects.all()
        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        column_data = self.json_data.get("columns", [])

        try:

            host_search = column_data[1]["search"]["value"].strip()
            mac_search = column_data[2]["search"]["value"].strip()
            expired_search = column_data[3]["search"]["value"]
            ip_search = column_data[4]["search"]["value"].strip()
            vendor_search = column_data[5]["search"]["value"].strip()
            search = self.json_data.get("search_filter", "").strip()
            is_owner = self.json_data.get("owner_filter", None)

            # group_filter = self.json_data.get('group_filter', None)
            # user_filter = self.json_data.get('user_filter', None)

            if is_owner:
                if is_owner == "1":
                    qs = qs.by_owner(self.request.user)
                elif is_owner == "2":
                    qs = qs.by_owner(self.request.user, use_groups=True)

            search_list = search.strip().split(",") if search else []
            for search_item in search_list:
                search_str = ":".join(search_item.split(":")[1:])
                if not search_str:
                    continue
                if search_item.startswith("desc:"):
                    qs = qs.filter(description__icontains=search_str)
                elif search_item.startswith("user:"):
                    user = User.objects.filter(username__iexact=search_str).first()
                    if user:
                        qs = qs.by_owner(user)
                    else:
                        qs = qs.none()
                elif search_item.startswith("group:"):
                    group = Group.objects.filter(name__iexact=search_str).first()
                    if group:
                        qs = qs.by_group(group)
                    else:
                        qs = qs.none()
                elif search_item.startswith("name:"):
                    qs = qs.filter(hostname__startswith=search_str.lower())
                elif search_item.startswith("mac:"):
                    mac_str = search_str
                    # Replace garbage
                    rgx = re.compile("[:,-. ]")
                    mac_str = rgx.sub("", mac_search)
                    # Split to list to put back togethor with :
                    mac_str = re.findall("..", mac_str)
                    mac_str = ":".join(mac_str)
                    qs = qs.filter(mac__startswith=mac_str.lower())
                elif search_item.startswith("ip:"):
                    ip = search_str
                    ip_blocks = [_f for _f in ip.split(".") if _f]
                    if len(ip_blocks) < 4 or not ip_blocks[3]:
                        qs = qs.filter(
                            Q(addresses__address__istartswith=".".join(ip_blocks))
                            | Q(
                                leases__address__address__istartswith=".".join(
                                    ip_blocks
                                )
                            )
                        ).distinct()
                    else:
                        qs = qs.filter(
                            Q(addresses__address=ip) | Q(leases__address__address=ip)
                        ).distinct()
                elif search_item.startswith("net:"):
                    if search_str.endswith("/"):
                        qs = qs.none()
                    else:
                        qs = qs.filter(
                            addresses__address__net_contained_or_equal=search_str
                        ).distinct()
                elif search_item.startswith("fattr:"):
                    qs = qs.filter(freeform_attributes__value=search_str)
                elif search_item.startswith("sattr:"):
                    qs = qs.filter(
                        structured_attributes__structured_attribute_value__value=search_str
                    )
                elif search_item.startswith("atype:"):
                    qs = qs.filter(address_type_id=search_str)
                elif search_item:
                    like_search_term = search_item + "%"
                    cursor = connection.cursor()

                    if re.match("([0-9a-f]{2}[:.-]?){5}[0-9a-f]{2}", search_item):
                        omni_sql = """
                            SELECT hosts.mac from hosts
                                WHERE hosts.mac = %(search)s
                        """
                    else:
                        omni_sql = """
                            SELECT hosts.mac from <hosts>   </hosts>
                                WHERE hosts.mac::text LIKE %(lsearch)s OR hosts.hostname LIKE %(lsearch)s

                            UNION

                            SELECT hosts.mac from hosts
                                WHERE hosts.search_index @@ plainto_tsquery('pg_catalog.english', %(search)s)

                            UNION

                            SELECT DISTINCT dns_records.mac from dns_records
                                LEFT OUTER JOIN dns_records as d2 ON (dns_records.name = d2.text_content AND d2.tid = 5)
                                WHERE dns_records.name LIKE %(lsearch)s OR d2.name LIKE %(lsearch)s

                            UNION

                            SELECT addresses.mac from addresses
                                WHERE HOST(addresses.address) = %(search)s

                            UNION

                            SELECT DISTINCT addresses.mac from addresses
                                INNER JOIN dns_records ON addresses.address = dns_records.ip_content
                                WHERE dns_records.name LIKE %(lsearch)s

                            UNION

                            SELECT leases.mac from leases
                                WHERE HOST(leases.address) = %(search)s
                        """
                    cursor.execute(
                        omni_sql, {"lsearch": like_search_term, "search": search_item}
                    )
                    search_hosts = cursor.fetchall()
                    qs = qs.filter(mac__in=[host[0] for host in search_hosts])

            if host_search:
                if host_search.startswith("^"):
                    qs = qs.filter(hostname__startswith=host_search[1:].lower())
                if host_search.startswith("~"):
                    qs = qs.filter(hostname__iregex=r"%s" % host_search[1:])
                elif host_search.startswith("="):
                    qs = qs.filter(hostname__exact=host_search[1:].lower())
                else:
                    qs = qs.filter(hostname__contains=host_search.lower())
            if mac_search:
                # Replace garbage
                rgx = re.compile("[:,-. ]")
                mac_str = rgx.sub("", mac_search)
                # Split to list to put back togethor with :
                mac_str = iter(mac_str)
                mac_str = ":".join(
                    a + b for a, b in zip_longest(mac_str, mac_str, fillvalue="")
                )
                qs = qs.filter(mac__startswith=mac_str.lower())
            if vendor_search:
                qs = qs.extra(
                    where=[
                        "hosts.mac >= ouis.start and hosts.mac <= ouis.stop AND ouis.shortname ILIKE %s"
                    ],
                    params=["%%%s%%" % vendor_search],
                    tables=["ouis"],
                )
            if ip_search:
                if re.search("[a-zA-Z]", ip_search):
                    qs = qs.none()
                elif "/" in ip_search and len(ip_search.split("/")) > 1:
                    if ip_search.endswith("/"):
                        qs = qs.none()
                    else:
                        try:
                            qs = qs.filter(
                                Q(addresses__address__net_contained_or_equal=ip_search)
                                | Q(
                                    leases__address__address__net_contained_or_equal=ip_search,
                                    leases__ends__gt=timezone.now(),
                                )
                            ).distinct()
                        except ValueError:
                            # If netmask is not valid, fail silently
                            pass
                else:
                    ip = ip_search.split(":")[-1]
                    tail_dot = "." if ip[-1] == "." else ""
                    ip_blocks = [_f for _f in ip.split(".") if _f]
                    if len(ip_blocks) < 4 or not ip_blocks[3]:
                        qs = qs.filter(
                            Q(
                                addresses__address__istartswith=".".join(ip_blocks)
                                + tail_dot
                            )
                            | Q(
                                leases__address__address__istartswith=".".join(
                                    ip_blocks
                                )
                                + tail_dot,
                                leases__ends__gt=timezone.now(),
                            )
                        ).distinct()
                    else:
                        qs = qs.filter(
                            Q(addresses__address=ip)
                            | Q(
                                leases__address__address=ip,
                                leases__ends__gt=timezone.now(),
                            )
                        ).distinct()

            # if group_filter:
            #     group = Group.objects.filter(pk=group_filter).first()
            #     if group:
            #         qs = qs.by_group(group)
            # if user_filter:
            #     user = User.objects.filter(pk=user_filter).first()
            #     if user:
            #         qs = qs.by_owner(user)

            if expired_search and expired_search == "1":
                qs = qs.filter(expires__gt=timezone.now())
            elif expired_search and expired_search == "0":
                qs = qs.filter(expires__lt=timezone.now())

        except (DatabaseError, ValidationError):
            pass

        return qs

    def raw_ordering(self):
        order_columns = (
            "hosts.mac",
            "hosts.hostname",
            "hosts.mac",
            "hosts.expires",
            "first_address",
        )

        # Number of columns that are used in sorting
        order_data = self.json_data.get("order", [])

        order = []
        for item in order_data:
            column = item["column"]
            column_dir = item["dir"]
            sdir = "DESC" if column_dir == "desc" else "ASC"
            sortcol = order_columns[column]
            order.append("%s %s" % (sortcol, sdir))

        if order:
            return ",".join(order)
        else:
            return "hosts.hostname"

    def prepare_results(self, qs):
        qs_macs = [str(q.mac) for q in qs]

        if not qs_macs:
            value_qs = []
        else:

            def dictfetchall(cursor):
                "Returns all rows from a cursor as a dict"
                desc = cursor.description
                return [
                    dict(list(zip([col[0] for col in desc], row)))
                    for row in cursor.fetchall()
                ]

            c = connection.cursor()
            c.execute(
                """
                SELECT
                    hosts.mac, hosts.hostname, hosts.expires, disabled.mac AS disabled, array_agg(host(addresses.address)) AS address, array_agg(host(leases.address)) AS lease,
                    coalesce(min(addresses.address), min(leases.address)) as first_address,
                    array_agg(leases.ends) AS ends, array_agg(gul_recent_arp_byaddress.stopstamp) AS ip_stamp,
                    (SELECT ouis.shortname from ouis WHERE hosts.mac >= ouis.start AND hosts.mac <= ouis.stop ORDER BY ouis.id DESC LIMIT 1) AS vendor,
                    (SELECT MAX(stopstamp) FROM gul_recent_arp_bymac WHERE hosts.mac = gul_recent_arp_bymac.mac) AS mac_stamp
                FROM hosts
                    LEFT OUTER JOIN addresses ON hosts.mac = addresses.mac
                    LEFT OUTER JOIN gul_recent_arp_byaddress ON addresses.address = gul_recent_arp_byaddress.address
                    LEFT OUTER JOIN leases ON hosts.mac = leases.mac
                    LEFT OUTER JOIN disabled ON hosts.mac = disabled.mac
                    LEFT OUTER JOIN ouis ON hosts.mac >= ouis.start AND hosts.mac <= ouis.stop
                WHERE hosts.mac IN %%s
                GROUP BY hosts.mac, hosts.hostname, hosts.expires, disabled.mac
                ORDER BY %s
            """
                % self.raw_ordering(),
                [tuple(qs_macs)],
            )
            value_qs = dictfetchall(c)

        user = self.request.user
        user_change_permissions = Host.objects.filter(pk__in=qs_macs).by_change_perms(
            user, ids_only=True
        )
        global_delete_permission = user.has_perm("hosts.delete_host")
        global_change_permission = user.has_perm("hosts.change_host")

        def get_last_mac_stamp(host):
            mac_stamp = host["mac_stamp"]
            if mac_stamp:
                mac_stamp = max(mac_stamp) if isinstance(mac_stamp, list) else mac_stamp
                return timezone.localtime(mac_stamp).strftime("%Y-%m-%d %I:%M %p")
            else:
                return None

        def get_last_ip_stamp(host):
            ip_stamp = host["ip_stamp"]
            ip_stamp = [ip_stamp] if not isinstance(ip_stamp, list) else ip_stamp
            ip_stamp = [stamp for stamp in ip_stamp if stamp is not None]
            if ip_stamp:
                return timezone.localtime(max(ip_stamp)).strftime("%Y-%m-%d %I:%M %p")
            else:
                return None

        def get_last_ip(host):
            if host.is_dynamic:
                leases = host.leases.all()
                if leases:
                    return str(leases[0].address)
                else:
                    return None
            else:
                addresses = host.addresses.all()
                if addresses:
                    return str(addresses[0])
                else:
                    return None

        def get_ips(host):
            addresses = []
            host["address"] = (
                [host["address"]]
                if not isinstance(host["address"], list)
                else host["address"]
            )
            host["lease"] = (
                [host["lease"]]
                if not isinstance(host["lease"], list)
                else host["lease"]
            )
            host["ends"] = (
                [host["ends"]] if not isinstance(host["ends"], list) else host["ends"]
            )
            if host["address"]:
                for address in host["address"]:
                    if address and address not in addresses:
                        addresses.append(address)
            if host["lease"]:
                for index, lease in enumerate(host["lease"]):
                    if lease and lease not in addresses:
                        try:
                            if (
                                host["ends"][index]
                                and host["ends"][index] > timezone.now()
                            ):
                                addresses.append(lease)
                        except IndexError:
                            pass

            if addresses:
                if len(addresses) == 1:
                    return "<span>%s</span>" % addresses[0]
                else:
                    return """
                        <span>%s</span>
                        <span>(<a href="javascript:void(0);" title="%s">%s</a>)</span>
                    """ % (
                        addresses[0],
                        "\n".join(addresses),
                        len(addresses),
                    )
            else:
                return '<span class="flagged">No Data</span>'

        def get_expires(expires):
            if expires < timezone.now():
                return '<span class="flagged">%s</span>' % timezone.localtime(
                    expires
                ).strftime("%Y-%m-%d")
            else:
                return timezone.localtime(expires).strftime("%Y-%m-%d")

        def get_selector(host, change_permissions):
            if change_permissions or global_delete_permission:
                return (
                    '<input class="action-select" name="selected_hosts" type="checkbox" value="%s" />'
                    % host["mac"]
                )
            else:
                return ""

        def render_cell(value, is_flagged=False, is_disabled=False):
            flagged = "flagged" if is_flagged else ""
            no_data = '<span class="%s">No Data</span>' % flagged
            return value if value else no_data

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for host in value_qs:
            is_disabled = "disabled" if host["disabled"] else ""

            if not is_disabled and (
                global_change_permission or host["mac"] in user_change_permissions
            ):
                change_permissions = True
            else:
                change_permissions = False
            host_view_href = reverse_lazy("view_host", args=(slugify(host["mac"]),))
            host_edit_href = reverse_lazy("update_host", args=(slugify(host["mac"]),))
            host_ips = get_ips(host)
            expires = get_expires(host["expires"])
            last_mac_stamp = get_last_mac_stamp(host)
            last_ip_stamp = get_last_ip_stamp(host)

            if not host_ips:
                is_flagged = True
            else:
                is_flagged = False if last_ip_stamp or last_mac_stamp else True

            json_data.append(
                [
                    get_selector(host, change_permissions),
                    (
                        '<a href="%(view_href)s" rel="%(hostname)s" id="%(update_href)s"'
                        ' class="host-details %(is_disabled)s" data-toggle="modal">'
                        '<span class="glyphicon glyphicon-chevron-right"></span> %(hostname)s</a>'
                        % {
                            "hostname": host["hostname"] or "N/A",
                            "view_href": host_view_href,
                            "update_href": host_edit_href,
                            "is_disabled": is_disabled,
                        }
                    ),
                    host["mac"],
                    expires,
                    host_ips,
                    host["vendor"],
                    render_cell(last_mac_stamp, is_flagged, is_disabled),
                    render_cell(last_ip_stamp, is_flagged, is_disabled),
                    '<a href="%s?q=host:%s">DNS Records</a>'
                    % (reverse_lazy("list_dns"), host["hostname"]),
                    '<a href="%s">%s</a>'
                    % (
                        host_edit_href if change_permissions else host_view_href,
                        "Edit" if change_permissions else "View",
                    ),
                ]
            )
        return json_data


class HostRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        pk = "".join(re.split("[^a-zA-Z0-9]*", kwargs["pk"]))
        self.url = reverse_lazy("update_host", kwargs={"pk": pk})
        return super(HostRedirectView, self).get_redirect_url(*args, **kwargs)


class HostListView(PermissionRequiredMixin, TemplateView):
    permission_required = "hosts.view_host"
    template_name = "hosts/host_list.html"

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)

        owner_filter = self.request.COOKIES.get("owner_filter", None)
        context["owner_filter"] = self.request.GET.get("mine", owner_filter)
        search_filter = self.request.COOKIES.get("search_filter")
        search_filter = urlunquote(search_filter).split(",") if search_filter else []
        context["search_filter"] = search_filter
        context["owners_form"] = HostOwnerForm()
        context["renew_form"] = HostRenewForm(user=self.request.user)
        context["rename_form"] = HostRenameForm()
        context["network_form"] = HostNetworkForm()
        context["attribute_qs"] = Attribute.objects.all()
        context["dhcp_group_form"] = HostDhcpGroupForm()
        context["attribute_delete_from"] = HostAttributesDeleteForm()

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(HostListView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        action = request.POST.get("action", None)
        selected_hosts = request.POST.getlist("selected_hosts", [])
        response = None

        if selected_hosts:
            selected_hosts = Host.objects.filter(pk__in=selected_hosts)

            # If action is to change owners on host(s)
            if action == "replace-owners":
                assign_owner_hosts(request, selected_hosts)
            elif action == "add-owners":
                assign_owner_hosts(request, selected_hosts, add_only=True)
            elif action == "remove-owners":
                remove_owner_hosts(request, selected_hosts)
            elif action == "delete":
                delete_hosts(request, selected_hosts)
            elif action == "export":
                response = export_csv(request, selected_hosts)
            elif action == "dns":
                populate_primary_dns(request, selected_hosts)
            elif action == "renew":
                renew_hosts(request, selected_hosts)
            elif action == "rename":
                rename_hosts(request, selected_hosts)
            elif action == "rename-confirm":
                rename_hosts(request, selected_hosts)
            elif action == "add-attributes":
                add_attribute_to_hosts(request, selected_hosts)
            elif action == "delete-attributes":
                delete_attribute_from_host(request, selected_hosts)
            elif action == "set-dhcpgroup":
                set_dhcp_group_on_host(request, selected_hosts)
            elif action == "change-network":
                change_network_on_host(request, selected_hosts)
            elif action == "delete-dhcpgroup":
                delete_dhcp_group_on_host(request, selected_hosts)

        if response:
            return response
        else:
            return redirect("list_hosts")


class HostDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "hosts.view_host"
    model = Host
    noaccess = False

    def get(self, request, *args, **kwargs):
        return super(HostDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostDetailView, self).get_context_data(**kwargs)
        attributes = []
        attributes += self.object.freeform_attributes.values_list(
            "attribute__description", "value"
        )
        attributes += self.object.structured_attributes.values_list(
            "structured_attribute_value__attribute__description",
            "structured_attribute_value__value",
        )
        context["read_only"] = self.kwargs.get("read_only", False)
        context["attributes"] = attributes
        context["dns_records"] = self.object.get_dns_records()
        context["addresses"] = self.object.addresses.select_related().all()
        context["pools"] = self.object.pools.all()
        context["leased_addresses"] = self.object.leases.select_related(
            "address", "host"
        ).all()
        context["user_owners"], context["group_owners"] = self.object.get_owners()
        context["disabled_info"] = Disabled.objects.filter(pk=self.object.pk).first()
        context["disabled_website"] = CONFIG.get("DISABLED_HOSTS_WEBSITE")
        context["view_show_users"] = (
            True if self.object.user.has_perm("user.view_user") else False
        )

        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return ["hosts/inc/detail.html"]
        else:
            return super(HostDetailView, self).get_template_names()

    def dispatch(self, request, *args, **kwargs):
        return super(HostDetailView, self).dispatch(request, *args, **kwargs)


class HostUpdateCreateMixin(object):
    model = Host
    form_class = HostForm
    success_url = reverse_lazy("list_hosts")

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        new = self.kwargs.get("new", False)
        if not new and self.request.session.get("host_form_add"):
            del self.request.session["host_form_add"]

        # passing the user object to the form here.
        return form_class(request=self.request, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(HostUpdateCreateMixin, self).get_context_data(**kwargs)
        context["dynamic_address_types"] = json.dumps(
            [
                address_type.pk
                for address_type in AddressType.objects.filter(pool__isnull=False)
            ]
        )
        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super(HostUpdateCreateMixin, self).post(request, *args, **kwargs)
        except ValidationError as e:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if not getattr(form, "_errors"):
                form._errors = ErrorDict()
            error_list = form._errors.setdefault(NON_FIELD_ERRORS, ErrorList())

            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)

            error_list.append("Please try again.")
            return self.form_invalid(form)


class HostUpdateView(HostUpdateCreateMixin, UpdateView):
    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        return super(HostUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostUpdateView, self).get_context_data(**kwargs)
        context["disabled_info"] = Disabled.objects.filter(pk=self.object.pk).first()
        context["disabled_website"] = CONFIG.get("DISABLED_HOSTS_WEBSITE")
        return context

    def get(self, request, *args, **kwargs):
        return super(HostUpdateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        original_object = serializers.serialize("json", [self.object])
        valid_form = super(HostUpdateView, self).form_valid(form)

        LogEntry.objects.log_action(
            user_id=self.object.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_text(self.object),
            action_flag=CHANGE,
            change_message=original_object,
        )
        messages.success(
            self.request,
            mark_safe(
                'Host <a href="%s" class="text-success"><strong>%s</strong></a> was successfully changed.'
                % (
                    reverse_lazy("update_host", args=[self.object.mac_stripped]),
                    self.object.hostname,
                )
            ),
        )

        if self.request.POST.get("_continue"):
            return redirect(
                reverse_lazy("update_host", kwargs={"pk": slugify(self.object.pk)})
            )

        return valid_form


class HostCreateView(PermissionRequiredMixin, HostUpdateCreateMixin, CreateView):
    permission_required = "hosts.add_host"

    def form_valid(self, form):
        valid_form = super(HostCreateView, self).form_valid(form)

        LogEntry.objects.log_action(
            user_id=self.object.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_text(self.object),
            action_flag=ADDITION,
        )

        messages.success(
            self.request,
            mark_safe(
                'Host <a href="%s" class="text-success"><strong>%s</strong></a> was successfully changed.'
                % (
                    reverse_lazy("update_host", args=[self.object.mac_stripped]),
                    self.object.hostname,
                )
            ),
        )

        if self.request.POST.get("_continue"):
            return redirect(
                reverse_lazy("update_host", kwargs={"pk": slugify(self.object.pk)})
            )
        elif self.request.POST.get("_add"):
            # Get fields that would carry over
            self.request.session["host_form_add"] = form.data
            return redirect(reverse_lazy("add_hosts_new"))

        return valid_form


class HostAddressCreateView(SuperuserRequiredMixin, DetailView):
    model = Host
    template_name = "hosts/host_address_form.html"

    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_static is False:
            return redirect("update_host", pk=self.object.mac_stripped)
        return super(HostAddressCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostAddressCreateView, self).get_context_data(**kwargs)
        self.host_addresses = self.object.addresses.values_list("address", flat=True)
        self.addresses = Address.objects.filter(host=self.object).exclude(
            arecords__name=self.object.hostname
        )
        if not self.addresses:
            self.addresses = Address.objects.filter(host=self.object)

        addresses_data = []
        for address in self.addresses:
            name = address.arecords.filter(
                Q(dns_type__name="A") | Q(dns_type__name="AAAA")
            ).first()
            addresses_data.append({"ip_address": address.address, "name": name})
        context["address_data"] = addresses_data

        return context

    def post(self, request, *args, **kwargs):
        new_addresses = request.POST.getlist("new-address", [])
        new_names = request.POST.getlist("new-hostname", [])
        new_ips = request.POST.getlist("new-ip", [])
        new_networks = request.POST.getlist("new-network", [])

        host = self.object
        context = self.get_context_data(object=self.object)
        data = context["form_data"] = []
        error_list = []

        try:
            for index, address in enumerate(new_addresses):
                if new_names[index] or new_networks[index] or new_ips[index]:
                    context["form_data"].append(
                        {
                            "a_type": request.POST.get("new-type-%s" % index),
                            "hostname": new_names[index],
                            "ip_address": new_ips[index],
                            "network": new_networks[index],
                        }
                    )

            for address in data:
                with transaction.atomic():
                    added_address = host.add_ip_address(
                        user=request.user,
                        ip_address=address["ip_address"] or None,
                        network=address["network"] or None,
                        hostname=address["hostname"] or None,
                    )
                messages.info(
                    request,
                    "Address %s has been assigned to Host %s"
                    % (added_address.address, host.hostname),
                )

        except ValidationError as e:
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(str(error))
            else:
                error_list.append(str(e.message))

            error_list.append("Please try again.")
            messages.error(request, mark_safe("<br />".join(error_list)))
            return render(request, self.template_name, context)

        return redirect("add_addresses_host", pk=host.mac_stripped)


class HostAddressDeleteView(SuperuserRequiredMixin, View):
    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        return super(HostAddressDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        host = get_object_or_404(Host, pk=self.kwargs.get("pk"))
        address = request.GET.get("address", None)
        if address:
            try:
                # Release address and delete DSN records.
                host.delete_ip_address(user=request.user, address=address)
            except ValidationError:
                return redirect("add_addresses_host", pk=host.mac_stripped)

            messages.info(
                request, "Address %s has been removed and released." % address
            )
        return redirect("add_addresses_host", pk=host.mac_stripped)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class HostBulkCreateView(PermissionRequiredMixin, FormView):
    permission_required = "hosts.add_host"
    template_name = "hosts/host_form_bulk.html"
    form_class = HostBulkCreateForm

    @staticmethod
    def host_to_dict(host):
        fields = [
            "hostname",
            "mac",
            "expire_days",
            "description",
            "ip_address",
            "network",
            "pool",
            "dhcp_group",
            "user_owners",
            "group_owners",
            "location",
        ]

        if len(host) < 3:
            raise ValidationError(
                "CSV File needs at least 3 columns: Hostname, MAC Address, and Expire Days."
            )

        host_vals = collections.OrderedDict()

        for i in range(len(host)):
            if host[i]:
                host_vals[fields[i]] = host[i].strip()

        return host_vals

    def form_valid(self, form):
        hosts = []
        csv_file = form.cleaned_data["csv_file"]
        lines = csv_file.read().decode("utf-8").splitlines()
        # with csv.open() as f:
        records = csv.reader(lines)
        for row in records:
            hosts.append(row)
        csv_file.close()

        required_fields = ["hostname", "mac", "expire_days"]

        # Check for unique hostnames and mac addresses
        macs, hostnames = [], []
        for host in hosts:
            hostnames.append(host[0])
            macs.append(host[1])

        error_list = []
        host = {}
        try:
            if len(hostnames) != len(set(hostnames)):
                raise ValidationError(
                    "Duplicate Hostnames detected.  Please make sure all hostnames are unique."
                )

            mac_dups = set([x for x in macs if macs.count(x) > 1])
            if mac_dups:
                raise ValidationError(
                    f"Duplicate Mac Addresses detected.  ({','.join(mac_dups)})  Please make sure all mac addresses are unique."
                )

            with transaction.atomic():
                for i in range(len(hosts)):
                    host = self.host_to_dict(hosts[i])

                    for field in required_fields:
                        if field not in host:
                            raise ValidationError(
                                "Missing required field '%s' on row '%s'"
                                % (field, i + 1)
                            )

                    if (
                        "ip" in host
                        and ("network" in host or "pool" in host)
                        or "network" in host
                        and "pool" in host
                    ):
                        raise ValidationError(
                            "Cannot set more than one of network, pool, or ip"
                        )

                    if (
                        "ip_address" not in host
                        and "network" not in host
                        and "pool" not in host
                    ):
                        host["pool"] = "routable-dynamic"

                    if host["mac"] == "vmware":
                        host["mac"] = Host.objects.find_next_mac(vendor="vmware")

                    if "user_owners" in host:
                        user_owners = host["user_owners"].split(",")
                        user_owners = [user.upper() for user in user_owners]
                        users_check = [
                            user.username
                            for user in User.objects.filter(username__in=user_owners)
                        ]
                        users_diff = set(user_owners) - set(users_check)
                        if users_diff:
                            raise ValidationError(
                                "Unknown User(s): %s" % ",".join(users_diff)
                            )
                        host["user_owners"] = user_owners

                    if "group_owners" in host:
                        group_owners = host["group_owners"].split(",")
                        groups_check = [
                            group.name
                            for group in Group.objects.filter(name__in=group_owners)
                        ]
                        groups_diff = set(group_owners) - set(groups_check)
                        if groups_diff:
                            raise ValidationError(
                                "Unknown Groups(s): %s" % ",".join(groups_diff)
                            )
                        host["group_owners"] = group_owners

                    try:
                        if "location" in host:
                            host_location = host["location"]
                            del host["location"]

                            instance = Host.objects.add_or_update_host(
                                self.request.user, **host
                            )

                            # Add location for attributes
                            FreeformAttributeToHost.objects.create(
                                host=instance,
                                attribute=Attribute.objects.get(name="location"),
                                value=host_location,
                                changed_by=self.request.user,
                            )
                    except Exception as e:
                        error_list.append("Error adding host from row %s" % (i + 1))
                        error_list.append(str(e))
                        raise ValidationError("")

        except ValidationError as e:
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append(str(error))
            else:
                error_list.append(str(e.message))

            pretty_print = []
            for k, v in list(host.items()):
                pretty_print.append("%s: %r" % (k, v))

            error_list.append("values: " + ", ".join(pretty_print))

            error_list.append("Please try again.")
            messages.error(self.request, mark_safe("<br />".join(error_list)))
            return redirect("add_hosts_bulk")
            # return render(self.request, self.template_name)

        messages.info(self.request, "Hosts from CSV have been added.")
        return redirect("list_hosts")


def change_owners(request):
    form = HostOwnerForm(request.POST or None)

    if form.is_valid:
        pass

    context = {"form": form}

    return render(request, "hosts/change_owners.html", context)
