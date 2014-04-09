from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.http import urlunquote
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.db.utils import DatabaseError
from django.contrib import messages
from django.forms.util import ErrorList
from django.db import transaction
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

from openipam.dns.models import DnsRecord, DnsType
from openipam.hosts.models import Host
from openipam.dns.forms import DNSListForm, DSNCreateFrom

from django_datatables_view.base_datatable_view import BaseDatatableView

from guardian.shortcuts import get_objects_for_user, get_objects_for_group

from netaddr.core import AddrFormatError

import json

User = get_user_model()


class DNSListJson(BaseDatatableView):
    order_columns = (
        'pk',
        'name',
        'ttl',
        'dns_type',
        'text_content',
        'dns_view',
    )

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 300

    def get_initial_queryset(self):
        qs = DnsRecord.objects.select_related('ip_content', 'dns_type', 'ip_content__host', 'domain').all()

        owner_filter = self.request.GET.get('owner_filter', None)
        if owner_filter:
            owner_permited_domains = get_objects_for_user(
                self.request.user,
                ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                any_perm=True
            )
            qs = qs.filter(domain__in=[domain.id for domain in owner_permited_domains])

        host = self.kwargs.get('host', '')
        if host:
            qs = qs.filter(
                Q(ip_content__host__hostname=host) |
                Q(text_content=host)
            )

        return qs

    def filter_queryset(self, qs):

        # use request parameters to filter queryset
        try:
            name_search = self.request.GET.get('sSearch_0', None)
            type_search = self.request.GET.get('sSearch_1', None)
            content_search = self.request.GET.get('sSearch_2', None)
            host_filter = self.request.GET.get('host_filter', None)
            search = self.request.GET.get('search_filter', None)
            group_filter = self.request.GET.get('group_filter', None)
            user_filter = self.request.GET.get('user_filter', None)

            search_list = search.strip().split(' ')
            for search_item in search_list:
                search_str = ''.join(search_item.split(':')[1:])
                if search_item.startswith('host:') and search_str:
                    qs = qs.filter(ip_content__host__hostname__istartswith=search_item[5:])
                elif search_item.startswith('mac:') and search_str:
                    mac_str = search_item[4:]
                    try:
                        mac_str = ':'.join(s.encode('hex') for s in mac_str.decode('hex'))
                    except TypeError:
                        pass
                    qs = qs.filter(ip_content__host__mac__istartswith=mac_str)
                elif search_item.startswith('ip:') and search_str:
                    qs = qs.filter(ip_content__address__istartswith=search_item[3:])
                elif search_item.startswith('user:') and search_str:
                    user = User.objects.filter(username__iexact=search_item[5:])
                    if user:
                        user_permited_domains = get_objects_for_user(
                            user[0],
                            ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                            any_perm=True
                        )
                        qs = qs.filter(domain__in=[domain.id for domain in user_permited_domains])
                    else:
                        qs = qs.none()
                elif search_item.startswith('group:') and search_str:
                    group = Group.objects.filter(name__iexact=search_item[6:])
                    if group:
                        group_permited_domains = get_objects_for_group(
                            group[0],
                            ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                            any_perm=True
                        )
                        qs = qs.filter(domain__in=[group.id for group in group_permited_domains])
                    else:
                        qs = qs.none()
                elif search_item:
                    qs = qs.filter(name__icontains=search_item)

            if name_search:
                qs = qs.filter(name__istartswith=name_search).distinct()
            if type_search:
                qs = qs.filter(dns_type=type_search)
            if content_search:
                qs = qs.filter(
                    Q(text_content__icontains=content_search) |
                    Q(ip_content__address__icontains=content_search)
                )
            if host_filter:
                host_filter = Host.objects.get(pk=host_filter)
                qs = qs.filter(
                    Q(ip_content__host=host_filter) |
                    Q(text_content__istartswith=host_filter.hostname)
                )
            if group_filter:
                group = Group.objects.get(pk=group_filter)
                group_permited_domains = get_objects_for_group(
                    group,
                    ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                    any_perm=True
                )
                qs = qs.filter(domain__in=[group.id for group in group_permited_domains])
            if user_filter:
                user = User.objects.get(pk=user_filter)
                user_permited_domains = get_objects_for_user(
                    user,
                    ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                    any_perm=True
                )
                qs = qs.filter(domain__in=[domain.id for domain in user_permited_domains])

        except DatabaseError:
            pass

        self.qs = qs

        return qs

    def prepare_results(self, qs):

        #user = self.request.user
        #group_perms = [domain.pk for domain in DomainGroupObjectPermission.objects.filter(group__in=user.groups.all())]
        #user_perms = [domain.pk for domain in DomainUserObjectPermission.objects.filter(user=user)]
        dns_types = DnsType.objects.exclude(min_permissions__name='NONE')

        def get_dns_types(dtype):
            #dns_types = DnsType.objects.exclude(min_permissions__name='NONE')
            types_html = []
            for dns_type in dns_types:
                if dns_type == dtype:
                    types_html.append(
                        '<option selected="selected" value="%s">%s</option>' % (dns_type.pk, dns_type.name)
                    )
                else:
                    types_html.append('<option value="%s">%s</option>' % (dns_type.pk, dns_type.name))
            return ''.join(types_html)

        def get_name(dns_record, has_permissions):
            html = '''
                <span>
                    <a href="%(view_href)s" rel="%(name)s">
                        %(name)s
                    </a>
                </span>
            '''
            if has_permissions:
                html += '<input type="text" name="name-%(id)s" value="%(name)s" style="display:none;" />'

            return html % {
                'id': dns_record.pk,
                'name': dns_record.name,
                'view_href': dns_view_href,
            },

        def get_type(dns_record, has_permissions):
            if not has_permissions:
                return '<span>%s</span>' % dns_record.dns_type.name
            else:
                return '''
                    <span>%s</span>
                    <select name="type-%s" style="display:none;">
                        %s
                    </select>
                ''' % (dns_record.dns_type.name, dns_record.pk, get_dns_types(dns_record.dns_type)),

        def get_content(dns_record, has_permissions):
            if dns_record.dns_type.is_a_record:
                content = str(dns_record.ip_content.address)
            elif dns_record.dns_type.is_mx_record or dns_record.dns_type.is_srv_record:
                content = '%s %s' % (dns_record.priority, dns_record.text_content)

            else:
                content = dns_record.text_content

            if len(content) > 100:
                s_content = content[:100] + '...'
            else:
                s_content = content

            if not has_permissions:
                return '<span title="%s">%s</span>' % (content, s_content)
            else:
                return '''
                <span title="%s">%s</span>
                <input type="text" class="dns-content" name="content-%s" value="%s" style="display:none;" />
            ''' % (content, s_content, dns_record.pk, content)

        def get_ttl(dns_record, has_permissions):
            if not has_permissions:
                return '<span>%s</span>' % dns_record.ttl
            else:
                return '''
                <span>%s</span>
                <input type="text" class="dns-ttl" name="ttl-%s" value="%s" style="display:none;" />
            ''' % (dns_record.ttl, dns_record.pk, dns_record.ttl)


        def get_links(dns_record, has_permissions):
            if has_permissions:
                return '''
                    <a href="javascript:void(0);" class="edit-dns" rel="%s">Edit</a>
                    <a href="javascript:void(0);" class="cancel-dns" rel="%s" style="display:none;">Cancel</a>
                ''' % (dns_record.pk, dns_record.pk)
            else:
                return ''

        def get_dns_view_href(dns_record):
            name_list = dns_record.name.split('.')
            for i, value, in enumerate(name_list):
                if value.startswith('*') or value.startswith('_'):
                    name_list[i] = ''
            name_list = [name for name in name_list if name]
            href = '.'.join(name_list)
            return reverse_lazy('list_dns', args=(href,))

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        user = self.request.user

        for dns_record in qs:
            has_permissions = dns_record.user_has_ownership(user)
            dns_view_href = get_dns_view_href(dns_record)
            json_data.append([
                ('<input class="action-select" name="selected-records" type="checkbox" value="%s" />'
                    % dns_record.pk) if has_permissions else '',
                get_name(dns_record, has_permissions),
                get_ttl(dns_record, has_permissions),
                get_type(dns_record, has_permissions),
                get_content(dns_record, has_permissions),
                dns_record.dns_view.name if dns_record.dns_view else '',
                get_links(dns_record, has_permissions),
            ])
        return json_data


class DNSListView(TemplateView):
    template_name = 'dns/dnsrecord_list.html'

    def get_context_data(self, **kwargs):
        context = super(DNSListView, self).get_context_data(**kwargs)
        context['dns_types'] = DnsType.objects.exclude(min_permissions__name='NONE')

        context['owner_filter'] = self.request.COOKIES.get('owner_filter', None)
        context['search_filter'] = urlunquote(self.request.COOKIES.get('search_filter', ''))

        data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
        if data_table_state:
            context.update(json.loads(data_table_state))

        selected_records = self.request.POST.getlist('selected-records', [])
        if selected_records:
            context['selected_records'] = json.dumps(selected_records)
            context['form_data'] = json.dumps(self.request.POST)
        new_records = self.request.POST.getlist('new-records', [])

        if new_records:
            context['form_data_new'] = []

            for index, value in enumerate(new_records):
                name_new = self.request.POST.getlist('name-new')[index]
                content_new = self.request.POST.getlist('content-new')[index]
                type_new = self.request.POST.getlist('type-new')[index]

                if name_new or content_new or type_new:
                    context['form_data_new'].append({
                        'name': name_new,
                        'content': content_new,
                        'type': type_new,
                    })

        return context

    # def dispatch(self, *args, **kwargs):
    #     host = self.kwargs.get('host', None)
    #     host = get_object_or_404(Host, hostname=host) if host else None
    #     return super(DNSListView, self).dispatch(*args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = request.user
        action = request.POST.get('action', None)
        selected_records = request.POST.getlist('selected-records', [])

        new_records = request.POST.getlist('new-records', [])
        new_names = request.POST.getlist('name-new', [])
        new_contents = request.POST.getlist('content-new', [])
        new_types = request.POST.getlist('type-new', [])
        new_ttls = request.POST.getlist('ttl-new', [])

        error_list = []

        if action == 'delete':

            for record in selected_records:
                LogEntry.objects.log_action(
                    user_id=self.request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(DnsRecord).pk,
                    object_id=record,
                    object_repr=force_unicode(DnsRecord.objects.get(pk=record)),
                    action_flag=DELETION
                )

            DnsRecord.objects.filter(pk__in=selected_records).delete()
            messages.success(self.request, "Selected DNS records have been deleted.")

            return redirect('list_dns')

        else:

            # New records
            for index, record in enumerate(new_records):
                if not new_names[index] and not new_contents[index] and not new_types[index]:
                    continue

                try:

                    dns_record, created = DnsRecord.objects.add_or_update_record(
                        user=self.request.user,
                        name=new_names[index],
                        content=new_contents[index],
                        dns_type=DnsType.objects.get(pk=int(new_types[index])),
                        ttl=new_ttls[index]
                    )

                    if dns_record:
                        LogEntry.objects.log_action(
                            user_id=self.request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(DnsRecord).pk,
                            object_id=dns_record.pk,
                            object_repr=force_unicode(dns_record),
                            action_flag=ADDITION
                        )

                except ValidationError, e:
                    if hasattr(e, 'error_dict'):
                        for key, errors in e.message_dict.items():
                            for error in errors:
                                error_list.append(error)
                    else:
                        error_list.append(e.message)
                    continue

            # Updated records
            for record in selected_records:
                try:

                    dns_record, created = DnsRecord.objects.add_or_update_record(
                        user=self.request.user,
                        name=request.POST.get('name-%s' % record, ''),
                        content=request.POST.get('content-%s' % record, ''),
                        dns_type=DnsType.objects.get(pk=int(request.POST.get('type-%s' % record, ''))),
                        ttl=request.POST.get('ttl-%s' % record, ''),
                        record=record
                    )

                    if dns_record:
                        LogEntry.objects.log_action(
                            user_id=self.request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(DnsRecord).pk,
                            object_id=dns_record.pk,
                            object_repr=force_unicode(dns_record),
                            action_flag=CHANGE
                        )

                except ValidationError, e:
                    if hasattr(e, 'error_dict'):
                        for key, errors in e.message_dict.items():
                            for error in errors:
                                error_list.append(error)
                    else:
                        error_list.append(e.message)
                    continue

            if error_list:
                error_list.append('Please try again.')
                messages.error(self.request, mark_safe('<br />'.join(error_list)))
            else:
                messages.success(self.request, "Selected DNS records have been updated.")
                return redirect('list_dns')

        return self.get(request, *args, **kwargs)


class DNSCreateView(FormView):
    template_name = 'dns/dnsrecord_form.html'
    form_class = DSNCreateFrom
    success_url = reverse_lazy('list_dns')

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            error_list = []
            try:
                DnsRecord.objects.add_or_update_record(
                    user=self.request.user,
                    name=form.cleaned_data['name'],
                    content=form.cleaned_data['content'],
                    dns_type=form.cleaned_data['dns_type'],
                    ttl=form.cleaned_data['ttl']
                )
            except ValidationError, e:
                if hasattr(e, 'error_dict'):
                    for key, errors in e.message_dict.items():
                        for error in errors:
                            error_list.append(error)
                else:
                    error_list.append(e.message)

            if error_list:
                errors = form._errors.setdefault("__all__", ErrorList(error_list))
                return self.form_invalid(form)
            else:
                messages.success(self.request, "DNS record has been added.")
                if request.POST.get('_add'):
                    return redirect('add_dns')
                else:
                    return redirect('list_dns')
        else:
            return self.form_invalid(form)


def index(request):
    return render(request, 'dns/index.html', {})
