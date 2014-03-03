from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.http import urlunquote
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.db.utils import DatabaseError
from django.contrib import messages
from django.db import transaction
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

from openipam.dns.models import DnsRecord, DnsType
from openipam.hosts.models import Host
from openipam.network.models import Address
from openipam.dns.forms import DNSListForm

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
                if search_item.startswith('host:'):
                    qs = qs.filter(ip_content__host__hostname__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('mac:'):
                    mac_str = search_item.split(':')
                    mac_str.pop(0)
                    mac_str = ''.join(mac_str)
                    try:
                        mac_str = ':'.join(s.encode('hex') for s in mac_str.decode('hex'))
                    except TypeError:
                        pass
                    qs = qs.filter(ip_content__host__mac__istartswith=mac_str)
                elif search_item.startswith('ip:'):
                    qs = qs.filter(ip_content__address__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('user:'):
                    user = User.objects.filter(username__iexact=search_item.split(':')[-1])
                    if user:
                        user_permited_domains = get_objects_for_user(
                            user[0],
                            ['dns.is_owner_domain', 'dns.add_records_to_domain'],
                            any_perm=True
                        )
                        qs = qs.filter(domain__in=[domain.id for domain in user_permited_domains])
                    else:
                        qs = qs.none()
                elif search_item.startswith('group:'):
                    group = Group.objects.filter(name__iexact=search_item.split(':')[-1])
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
                qs = qs.filter(name__icontains=name_search).distinct()
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
                    Q(text_content__icontains=host_filter.hostname)
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
                content = dns_record.ip_content.address
            elif dns_record.dns_type.is_mx_record or dns_record.dns_type.is_srv_record:
                content = '%s %s' % (dns_record.priority, dns_record.text_content)
            else:
                content = dns_record.text_content

            if not has_permissions:
                return '<span>%s</span>' % content
            else:
                return '''
                <span>%s</span>
                <input type="text" class="dns-content" name="content-%s" value="%s" style="display:none;" />
            ''' % (content, dns_record.pk, content)

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
                dns_record.ttl,
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
            def add_or_update_record(record_data, record=None):
                try:
                    if record:
                        dns_record = DnsRecord.objects.get(pk=record)
                    else:
                        dns_record = DnsRecord()

                    record_type = int(record_data['record_type']) if record_data['record_type'] else 0
                    record_type = DnsType.objects.get(pk=record_type)
                    dns_record.dns_type = record_type

                    if record_type.is_a_record:
                        if not record_data['record_content']:
                            error_list.append('IP content for A records connot be blank.')
                        else:
                            address = Address.objects.get(address=record_data['record_content'])
                            dns_record.ip_content = address
                    else:
                        dns_record.text_content = record_data['record_content']
                        if record_type.is_mx_record or record_type.is_srv_record:
                            parsed_content = record_data['record_content'].strip().split(' ')
                            if len(parsed_content) != 2:
                                error_list.append('Content for MX records need to only have a priority and FQDN.')
                            else:
                                dns_record.set_priority()

                    dns_record.name = record_data['record_name']
                    dns_record.set_domain_from_name()
                    dns_record.changed_by = request.user

                    dns_record.full_clean()

                    if not dns_record.user_has_ownership(request.user):
                        raise ValidationError('Invalid credentials: user %s does not have permissions'
                                              ' to add/modify this record.' % request.user)
                    if not error_list:
                        dns_record.save()
                        return dns_record

                except AddrFormatError:
                    error_list.append('Invalid IP for content: %s' % record_data['record_content'])

                except DnsType.DoesNotExist:
                    error_list.append('Invalid DNS Type for %s' % record_data['record_name'])

                except Address.DoesNotExist:
                    error_list.append('IP does not exist for content: %s' % record_data['record_content'])

                except ValidationError, e:
                    #assert False, dns_record.domain
                    for key, errors in e.message_dict.items():
                        for error in errors:
                            error_list.append(error)

                except:
                    raise

            # New records
            for index, record in enumerate(new_records):
                if not new_names[index] and not new_contents[index] and not new_types[index]:
                    continue

                record_data = {
                    'record_name': new_names[index],
                    'record_content': new_contents[index],
                    'record_type': new_types[index],
                }
                dns_resond = add_or_update_record(record_data)

                LogEntry.objects.log_action(
                    user_id=self.request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(dns_resond).pk,
                    object_id=dns_resond.pk,
                    object_repr=force_unicode(dns_resond),
                    action_flag=ADDITION
                )

            # Updated records
            for record in selected_records:

                record_type = request.POST.get('type-%s' % record, '')
                record_type = int(record_type) if record_type else 0
                record_data = {
                    'record_name': request.POST.get('name-%s' % record, ''),
                    'record_content': request.POST.get('content-%s' % record, ''),
                    'record_type': request.POST.get('type-%s' % record, ''),
                }
                dns_resond = add_or_update_record(record_data, record)

                LogEntry.objects.log_action(
                    user_id=self.request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(dns_resond).pk,
                    object_id=dns_resond.pk,
                    object_repr=force_unicode(dns_resond),
                    action_flag=CHANGE
                )

            if error_list:
                error_list.append('Please try again.')
                messages.error(self.request, mark_safe('<br />'.join(error_list)))
            else:
                messages.success(self.request, "Selected DNS records have been updated.")
                return redirect('list_dns')

        return self.get(request, *args, **kwargs)


class DNSCreateView(CreateView):
    pass


def index(request):
    return render(request, 'dns/index.html', {})
