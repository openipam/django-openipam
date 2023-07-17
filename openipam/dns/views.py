from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.http import urlunquote
from django.utils.html import conditional_escape
from django.db.utils import DatabaseError
from django.contrib import messages
from django.forms.utils import ErrorList
from django.db import transaction
from django.shortcuts import get_object_or_404

from openipam.dns.forms import DSNCreateFrom
from openipam.dns.models import DnsRecord, DnsType
from openipam.dns.actions import delete_records
from openipam.core.views import BaseDatatableView
from openipam.core.utils.messages import process_errors

from guardian.shortcuts import get_objects_for_user

from braces.views import PermissionRequiredMixin

from itertools import zip_longest

import json
import re

User = get_user_model()


class DNSListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = "dns.view_dnsrecord"

    order_columns = (
        "pk",
        "name",
        "ttl",
        "dns_type",
        "text_content",
        "host",
        "dns_view",
    )

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 1500

    def get_initial_queryset(self):
        qs = DnsRecord.objects.select_related(
            "ip_content", "dns_type", "ip_content__host", "domain"
        ).all()

        owner_filter = self.json_data.get("change_filter", None)
        if owner_filter:
            qs = qs.by_change_perms(self.request.user)

        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        column_data = self.json_data.get("columns", [])

        # use request parameters to filter queryset
        try:
            name_search = column_data[1]["search"]["value"]
            type_search = column_data[3]["search"]["value"]
            content_search = column_data[4]["search"]["value"]
            search = self.json_data.get("search_filter", "")

            # host_filter = self.json_data.get('host_filter', None)
            # group_filter = self.json_data.get('group_filter', None)
            # user_filter = self.json_data.get('user_filter', None)

            search_list = search.strip().split(" ") if search else []
            for search_item in search_list:
                search_str = "".join(search_item.split(":")[1:])
                if search_item.startswith("id:") and search_str:
                    qs = qs.filter(pk=search_item[3:].lower())
                elif search_item.startswith("host:") and search_str:
                    qs = qs.filter(
                        Q(
                            ip_content__host__hostname__startswith=search_item[
                                5:
                            ].lower()
                        )
                        | Q(text_content__iexact=search_item[5:])
                        | Q(name__iexact=search_item[5:])
                        | Q(host__hostname=search_item[5:])
                    )
                elif search_item.startswith("mac:") and search_str:
                    mac_str = search_item[4:]
                    try:
                        mac_str = ":".join(
                            s.encode("hex") for s in mac_str.decode("hex")
                        )
                    except TypeError:
                        pass
                    qs = qs.filter(ip_content__host__mac__startswith=mac_str.lower())
                elif search_item.startswith("ip:") and search_str:
                    qs = qs.filter(ip_content__address__startswith=search_item[3:])
                elif search_item.startswith("user:") and search_str:
                    user = User.objects.filter(username__iexact=search_item[5:]).first()
                    if user:
                        qs = qs.by_change_perms(user)
                    else:
                        qs = qs.none()
                elif search_item.startswith("group:") and search_str:
                    group = Group.objects.filter(name__iexact=search_item[6:]).first()
                    if group:
                        qs = qs.by_change_perms(group)
                    else:
                        qs = qs.none()
                elif search_item:
                    qs = qs.filter(name__contains=search_item.lower())

            if name_search:
                if name_search.startswith("~"):
                    qs = qs.filter(name__iregex=name_search[1:]).distinct()
                elif name_search.startswith("^"):
                    qs = qs.filter(name__istartswith=name_search[1:]).distinct()
                elif name_search.startswith("="):
                    qs = qs.filter(name__exact=name_search[1:]).distinct()
                else:
                    qs = qs.filter(name__icontains=name_search.lower()).distinct()
            if type_search:
                qs = qs.filter(dns_type=type_search)
            if content_search:
                # Replace garbage
                rgx = re.compile("[:,-. ]")
                content_str = rgx.sub("", content_search)
                # Split to list to put back togethor with :
                content_str = iter(content_str)
                content_str = ".".join(
                    a + b
                    for a, b in zip_longest(content_str, content_str, fillvalue="")
                )
                qs = qs.filter(
                    Q(text_content__icontains=content_str.lower())
                    | Q(ip_content__address__startswith=content_str.lower())
                )

            # if host_filter:
            #     host_filter = Host.objects.get(pk=host_filter)
            #     qs = qs.filter(
            #         Q(ip_content__host=host_filter) |
            #         Q(text_content__istartswith=host_filter.hostname)
            #     )
            # if group_filter:
            #     group = Group.objects.get(pk=group_filter)
            #     group_permited_domains = get_objects_for_group(
            #         group,
            #         ['dns.is_owner_domain', 'dns.add_records_to_domain'],
            #         any_perm=True
            #     )
            #     qs = qs.filter(domain__in=[group.id for group in group_permited_domains])
            # if user_filter:
            #     user = User.objects.get(pk=user_filter)
            #     user_permited_domains = get_objects_for_user(
            #         user,
            #         ['dns.is_owner_domain', 'dns.add_records_to_domain'],
            #         any_perm=True
            #     )
            #     qs = qs.filter(domain__in=[domain.id for domain in user_permited_domains])

        except (DatabaseError, ValidationError):
            pass

        self.qs = qs

        return qs

    def prepare_results(self, qs):
        change_permissions = (
            DnsRecord.objects.filter(pk__in=[record.pk for record in qs])
            .by_change_perms(self.request.user)
            .values_list("pk", flat=True)
        )
        global_delete_permission = self.request.user.has_perm("dns.delete_record")

        # Currently un-used
        # dns_types = get_objects_for_user(
        #     self.request.user,
        #     ["dns.add_records_to_dnstype", "dns.change_dnstype"],
        #     any_perm=True,
        #     use_groups=True,
        #     with_superuser=True,
        # )

        # def get_dns_types(dtype):
        #     types_html = []
        #     for dns_type in dns_types:
        #         if dns_type == dtype:
        #             types_html.append(
        #                 '<option selected="selected" value="%s">%s</option>' % (dns_type.pk, dns_type.name)
        #             )
        #         else:
        #             types_html.append('<option value="%s">%s</option>' % (dns_type.pk, dns_type.name))
        #     return "".join(types_html)

        def get_name(dns_record, has_change_permission):
            html = """
                <span>
                    <a href="%(view_href)s" rel="%(name)s">
                        %(name)s
                    </a>
                </span>
            """
            if has_change_permission:
                html += """<input type="text" name="name-%(id)s" value="%(name)s"
                class="form-control input-sm" style="display:none;" />"""

            return (
                html
                % {
                    "id": dns_record.pk,
                    "name": conditional_escape(dns_record.name),
                    "view_href": conditional_escape(dns_view_href),
                },
            )

        def get_type(dns_record, has_change_permission):
            # Disabling dns_type edits per ekoyle
            # if not has_change_permission:
            return '<span id="dns_type">%s</span>' % conditional_escape(
                dns_record.dns_type.name
            )
            # else:
            #     return '''
            #         <span>%s</span>
            #         <select name="type-%s" class="form-control input-sm" style="display:none;">
            #             %s
            #         </select>
            #     ''' % (dns_record.dns_type.name, dns_record.pk, get_dns_types(dns_record.dns_type)),

        def get_content(dns_record, has_change_permission):
            if dns_record.dns_type.is_a_record:
                content = str(dns_record.ip_content.address)
            elif dns_record.dns_type.is_mx_record or dns_record.dns_type.is_srv_record:
                content = "%s %s" % (dns_record.priority, dns_record.text_content)

            else:
                content = dns_record.text_content

            if len(content) > 100:
                s_content = content[:100] + "..."
            else:
                s_content = content

            if not has_change_permission:
                return '<span title="%s">%s</span>' % (
                    conditional_escape(content),
                    conditional_escape(s_content),
                )
            else:
                return """
                <span title="%s">%s</span>
                <input type="text"
                class="input-content dns-content form-control input-sm" name="content-%s"
                value="%s" style="display:none;" />
            """ % (
                    conditional_escape(content),
                    conditional_escape(s_content),
                    dns_record.pk,
                    conditional_escape(content),
                )

        def get_ttl(dns_record, has_change_permission):
            if not has_change_permission:
                return "<span>%s</span>" % dns_record.ttl
            else:
                return """
                <span>%s</span>
                <input type="text" class="dns-ttl form-control input-sm" name="ttl-%s"
                value="%s" style="display:none;" />
            """ % (
                    dns_record.ttl,
                    dns_record.pk,
                    dns_record.ttl,
                )

        def get_links(dns_record, has_change_permission):
            if has_change_permission:
                return """
                    <a href="javascript:void(0);" class="edit-dns" rel="%s">Edit</a>
                    <a href="javascript:void(0);" class="cancel-dns" rel="%s" style="display:none;">Cancel</a>
                """ % (
                    dns_record.pk,
                    dns_record.pk,
                )
            else:
                return ""

        def get_dns_view_href(dns_record):
            name_list = dns_record.name.split(".")
            for i, value in enumerate(name_list):
                if value.startswith("*") or value.startswith("_"):
                    name_list[i] = ""
            name_list = [name for name in name_list if name]
            href = ".".join(name_list)
            return reverse_lazy("core:dns:list_dns", args=(href,))

        def get_dns_host_href(dns_record):
            return '<a href="%s">Host</a>' % reverse_lazy(
                "core:hosts:view_host", args=(dns_record.host.mac_stripped,)
            )

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        for dns_record in qs:
            has_change_permission = (
                True if dns_record.pk in change_permissions else False
            )
            dns_view_href = get_dns_view_href(dns_record)
            data = [
                (
                    '<input class="action-select" name="selected-records" type="checkbox" value="%s" />'
                    % dns_record.pk
                ),
                get_name(dns_record, has_change_permission),
                get_ttl(dns_record, has_change_permission),
                get_type(dns_record, has_change_permission),
                get_content(dns_record, has_change_permission),
                get_dns_host_href(dns_record) if dns_record.host else "",
                dns_record.dns_view.name if dns_record.dns_view else "",
                get_links(dns_record, has_change_permission),
                "",
            ]
            json_data.append(
                data[0:8]
                if has_change_permission or global_delete_permission
                else data[1:]
            )
        return json_data


class DNSListView(PermissionRequiredMixin, TemplateView):
    permission_required = "dns.view_dnsrecord"
    template_name = "dns/dnsrecord_list.html"

    def get_context_data(self, **kwargs):
        context = super(DNSListView, self).get_context_data(**kwargs)
        context["dns_types_change"] = get_objects_for_user(
            self.request.user,
            ["dns.add_records_to_dnstype", "dns.change_dnstype"],
            any_perm=True,
            use_groups=True,
            with_superuser=True,
        )
        type_records = DnsRecord.objects.all().only("dns_type_id").values_list("id")
        context["dns_types"] = DnsType.objects.filter(id__in=type_records)

        change_filter = self.request.COOKIES.get("change_filter", None)
        context["change_filter"] = self.request.GET.get("mine", change_filter)
        if kwargs.get("host"):
            context["search_filter"] = "host:%s" % kwargs["host"]
        else:
            context["search_filter"] = urlunquote(
                self.request.COOKIES.get("search_filter", "")
            )

        selected_records = self.request.POST.getlist("selected-records", [])
        if selected_records:
            context["selected_records"] = json.dumps(selected_records)
            context["form_data"] = json.dumps(self.request.POST)
        new_records = self.request.POST.getlist("new-records", [])

        if new_records:
            context["form_data_new"] = []

            for index, value in enumerate(new_records):
                name_new = self.request.POST.getlist("name-new")[index]
                ttl_new = self.request.POST.getlist("ttl-new")[index]
                content_new = self.request.POST.getlist("content-new")[index]
                type_new = self.request.POST.getlist("type-new")[index]

                if name_new or content_new or type_new:
                    context["form_data_new"].append(
                        {
                            "name": name_new,
                            "ttl": ttl_new,
                            "content": content_new,
                            "type": type_new,
                        }
                    )

        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(DNSListView, self).render_to_response(
            context, **response_kwargs
        )
        if self.kwargs.get("host"):
            response.set_cookie(
                "search_filter",
                "host:%s" % self.kwargs["host"],
                path=reverse_lazy("core:dns:list_dns"),
            )
        return response

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", None)
        selected_records = request.POST.getlist("selected-records", [])

        new_records = request.POST.getlist("new-records", [])
        new_names = request.POST.getlist("name-new", [])
        new_contents = request.POST.getlist("content-new", [])
        new_types = request.POST.getlist("type-new", [])
        new_ttls = request.POST.getlist("ttl-new", [])

        error_list = []

        if action:
            if action == "delete":
                delete_records(request, selected_records)

            return redirect("core:dns:list_dns")
        else:
            # Permission checks are done inside add_or_update_record
            # New records
            for index, record in enumerate(new_records):
                if (
                    not new_names[index]
                    and not new_contents[index]
                    and not new_types[index]
                ):
                    continue

                try:
                    if not new_types[index]:
                        raise ValidationError("A Dns Type is required.")

                    dns_record, created = DnsRecord.objects.add_or_update_record(
                        user=request.user,
                        name=new_names[index],
                        content=new_contents[index],
                        dns_type=DnsType.objects.get(pk=int(new_types[index])),
                        ttl=new_ttls[index],
                    )

                except ValidationError as e:
                    if hasattr(e, "error_dict"):
                        for key, errors in list(e.message_dict.items()):
                            for error in errors:
                                error_list.append(str(error).capitalize())
                    else:
                        error_list.append(str(e.message).capitalize())
                    continue

            # Updated records
            for record in selected_records:
                try:
                    dns_record, created = DnsRecord.objects.add_or_update_record(
                        user=request.user,
                        name=request.POST.get("name-%s" % record, ""),
                        content=request.POST.get("content-%s" % record, ""),
                        ttl=request.POST.get("ttl-%s" % record, ""),
                        record=record,
                    )

                except ValidationError as e:
                    if hasattr(e, "error_dict"):
                        for key, errors in list(e.message_dict.items()):
                            for error in errors:
                                error_list.append(str(error).capitalize())
                    else:
                        error_list.append(str(e.message).capitalize())
                    continue

            if error_list:
                error_list = list(set(error_list))
                error_list.append("Please try again.")
                process_errors(request, error_list=error_list)
            else:
                messages.success(
                    self.request, "Selected DNS records have been updated."
                )
                return redirect("core:dns:list_dns")

        return self.get(request, *args, **kwargs)


class DNSCreateUpdateView(PermissionRequiredMixin, FormView):
    permission_required = "dns.add_record"
    template_name = "dns/dnsrecord_form.html"
    form_class = DSNCreateFrom
    success_url = reverse_lazy("core:dns:list_dns")
    record = None

    def get_context_data(self, **kwargs):
        if self.kwargs.get("pk"):
            kwargs["pk"] = self.kwargs.get("pk")
        if self.record:
            kwargs["object"] = self.record
        return super(DNSCreateUpdateView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get("pk"):
            self.record = get_object_or_404(DnsRecord, pk=kwargs.get("pk"))
            self.initial = {
                "name": self.record.name,
                "dns_type": self.record.dns_type,
                "ttl": self.record.ttl,
            }
            if self.record.dns_type.is_a_record:
                self.initial["content"] = self.record.ip_content.address
            else:
                self.initial["content"] = self.record.text_content

        return super(DNSCreateUpdateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            error_list = []
            try:
                DnsRecord.objects.add_or_update_record(
                    user=request.user,
                    name=form.cleaned_data["name"],
                    content=form.cleaned_data["content"],
                    dns_type=form.cleaned_data["dns_type"],
                    ttl=form.cleaned_data["ttl"],
                    record=self.record.pk if hasattr(self.record, "pk") else None,
                )
            except ValidationError as e:
                if hasattr(e, "error_dict"):
                    for key, errors in list(e.message_dict.items()):
                        for error in errors:
                            error_list.append(error)
                else:
                    error_list.append(e.message)

            if error_list:
                errors = form._errors.setdefault("__all__", ErrorList(error_list))
                return self.form_invalid(form)
            else:
                if self.record:
                    messages.success(self.request, "DNS record has been updated.")
                else:
                    messages.success(self.request, "DNS record has been added.")
                if request.POST.get("_add"):
                    return redirect("core:dns:add_dns")
                else:
                    return redirect("core:dns:list_dns")
        else:
            return self.form_invalid(form)
