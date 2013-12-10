from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.http import urlunquote
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.db.utils import DatabaseError
from django.contrib import messages

from openipam.dns.models import DnsRecord, DnsType, DomainUserObjectPermission, DomainGroupObjectPermission
from openipam.hosts.models import Host
from openipam.network.models import Address
from openipam.dns.forms import DNSListForm

from django_datatables_view.base_datatable_view import BaseDatatableView

from netaddr.core import AddrFormatError


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
    max_display_length = 100

    def get_initial_queryset(self):
        qs = DnsRecord.objects.all()

        host = self.kwargs.get('host', '')
        if host:
            qs = qs.filter(
                Q(ip_content__host__hostname=host) |
                Q(text_content__icontains=host)
            )

        return qs

    def filter_queryset(self, qs):

        # use request parameters to filter queryset
        try:
            search = self.request.GET.get('sSearch', None)
            name_search = self.request.GET.get('sSearch_0', None)
            type_search = self.request.GET.get('sSearch_1', None)
            content_search = self.request.GET.get('sSearch_2', None)
            host_filter = self.request.GET.get('host_filter', None)
            group_filter = self.request.GET.get('group_filter', None)
            user_filter = self.request.GET.get('user_filter', None)

            search_list = search.strip().split(' ')
            for search_item in search_list:
                if search_item.startswith('user:'):
                    qs = qs.filter(domain__user_permissions__user__username__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('name:'):
                    qs = qs.filter(name__startswith=search_item.split(':')[-1])
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
                else:
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
                hostname = Host.objects.get(pk=host_filter)
                qs = qs.filter(
                    Q(ip_content__host=host_filter) |
                    Q(text_content__icontains=hostname)
                )
            if group_filter:
                qs = qs.filter(domain__group_permissions__group__pk=group_filter)
            if user_filter:
                qs = qs.filter(domain__user_permissions__user__pk=user_filter)

        except DatabaseError:
            pass

        self.qs = qs

        return qs


    def prepare_results(self, qs):

        #user = self.request.user
        #group_perms = [domain.pk for domain in DomainGroupObjectPermission.objects.filter(group__in=user.groups.all())]
        #user_perms = [domain.pk for domain in DomainUserObjectPermission.objects.filter(user=user)]


        def get_dns_types(dtype):
            dns_types = DnsType.objects.exclude(min_permissions__name='NONE')
            types_html = []
            for dns_type in dns_types:
                if dns_type == dtype:
                    types_html.append('<option selected="selected" value="%s">%s</option>' % (dns_type.pk, dns_type.name))
                else:
                    types_html.append('<option value="%s">%s</option>' % (dns_type.pk, dns_type.name))
            return ''.join(types_html)

        def get_name(dns_record, has_permissions):
            html = '''
                <span>
                    <a href="%(view_href)s" rel="%(name)s" id="%(update_href)s">
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
                'update_href': dns_edit_href
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
            content = dns_record.ip_content.address if dns_record.ip_content else dns_record.text_content
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

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        user = self.request.user

        for dns_record in qs:
            has_permissions = dns_record.user_has_ownership(user)
            print has_permissions
            dns_view_href = '' #reverse_lazy('view_dns', args=(slugify(dns_record.pk),))
            dns_edit_href = '' #reverse_lazy('update_dns', args=(slugify(dns_record.pk),))
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



# def dns_list_edit(request):

#     search_string = request.GET.get('q', None)
#     mac_string = request.GET.get('mac', None)
#     page = request.GET.get('page', None)
#     queryset = DnsRecord.objects.none()
#     page_objects = None
#     DNSUpdateFormset = modelformset_factory(DnsRecord, DNSUpdateForm, formset=BaseDNSUpdateFormset, can_delete=True, extra=0)
#     host = None

#     if mac_string:
#         queryset = DnsRecord.objects.select_related('dns_type').filter(
#             address__host__mac=mac_string
#         )
#         host = Host.objects.get(mac=mac_string)

#     elif search_string:
#         queryset = DnsRecord.objects.select_related('dns_type').filter(
#             #Q(domain__name__istartswith=search_string) |
#             Q(name__istartswith=search_string) |
#             Q(text_content__istartswith=search_string)
#         )

#         paginator = Paginator(queryset, 50)
#         try:
#             page_objects = paginator.page(page)
#         except PageNotAnInteger:
#             page_objects = paginator.page(1)
#         except EmptyPage:
#             page_objects = paginator.page(paginator.num_pages)

#         # Paginated queryset for formset
#         queryset = queryset.filter(id__in=[object.id for object in page_objects])
#     else:
#         DNSUpdateFormset.extra = 1

#     formset = DNSUpdateFormset(user=request.user, data=request.POST or None, queryset=queryset)

#     if formset.is_valid():
#         instances = formset.save(commit=False)
#         for instance in instances:
#             instance.changed_by = request.user
#             instance.save()

#         messages.add_message(request, messages.INFO, 'DNS Entries have been saved.')

#         return redirect('%s?q=%s' % (reverse('list_dns'), search_string))

#     context = {
#         'host': host,
#         'queryset': queryset,
#         'page_objects': page_objects,
#         'formset': formset,
#     }

#     return render(request, 'dns/dnsrecord_list.html', context)


class DNSListView(TemplateView):
    template_name = 'dns/dnsrecord_list.html'

    def get_context_data(self, **kwargs):
        context = super(DNSListView, self).get_context_data(**kwargs)
        context['dns_types'] = DnsType.objects.exclude(min_permissions__name='NONE')
        context['form'] = DNSListForm()
        #DNSUpdateFormset = modelformset_factory(DnsRecord, DNSUpdateForm, can_delete=True)
        #context['formset'] = DNSUpdateFormset(queryset=context['object_list'])

        data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
        if data_table_state:
            context.update(simplejson.loads(data_table_state))

        selected_records = self.request.POST.getlist('selected-records', [])
        if selected_records:
            context['selected_records'] = simplejson.dumps(selected_records)
            context['form_data'] = simplejson.dumps(self.request.POST)

        #self.request.COOKIES['host_filter'] = self.host

        return context

    def dispatch(self, *args, **kwargs):
        host = self.kwargs.get('host', None)
        host = get_object_or_404(Host, hostname=host) if host else None
        return super(DNSListView, self).dispatch(*args, **kwargs)

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
            pass

        else:

            def add_or_update_record(record_data, record=None):
                try:
                    if record:
                        dns_record = DnsRecord.objects.get(pk=record)
                    else:
                        dns_record = DnsRecord()

                    record_type = int(record_data['record_type']) if record_data['record_type'] else 0
                    record_type = DnsType.objects.get(pk=record_type)

                    if record_type.is_a_record:
                        address = Address.objects.get(address=record_data['record_content'])
                        dns_record.ip_content = address
                    else:
                        dns_record.text_content = record_data['record_content']

                    dns_record.dns_type = record_type
                    dns_record.changed_by = request.user
                    dns_record.full_clean()
                    if not error_list:
                        dns_record.save()

                except AddrFormatError:
                    error_list.append('Invalid IP for content: %s' % record_data['record_content'])

                except DnsType.DoesNotExist:
                    error_list.append('Invalid DNS Type: %s' % record_data['record_content'])

                except Address.DoesNotExist:
                    error_list.append('IP does not exist for content: %s' % record_data['record_content'])

                except ValidationError, e:
                    for key, errors in e.message_dict.items():
                        for error in errors:
                            error_list.append(error)

            # New records
            for index, record in enumerate(new_records):
                if not new_names[index] and not new_contents[index] and not new_types[index]:
                    continue

                record_data = {
                    'record_name': new_names[index],
                    'record_content': new_contents[index],
                    'record_type': new_types[index],
                }
                add_or_update_record(record_data)

            # Updated records
            for record in selected_records:

                record_type = request.POST.get('type-%s' % record, '')
                record_type = int(record_type) if record_type else 0
                record_data = {
                    'record_name': request.POST.get('name-%s' % record, ''),
                    'record_content': request.POST.get('content-%s' % record, ''),
                    'record_type': request.POST.get('type-%s' % record, ''),
                }
                add_or_update_record(record_data, record)

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
