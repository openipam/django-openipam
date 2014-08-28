from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView, View
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.http import urlunquote
from django.utils import timezone
from django.utils.encoding import force_unicode
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
from django.forms.util import ErrorList, ErrorDict

from openipam.core.utils.merge_values import merge_values
from openipam.core.views import BaseDatatableView
from openipam.hosts.decorators import permission_change_host
from openipam.hosts.forms import HostForm, HostOwnerForm, HostRenewForm
from openipam.hosts.models import Host, Disabled
from openipam.network.models import AddressType, Lease, Address
from openipam.hosts.actions import delete_hosts, renew_hosts, assign_owner_hosts
from openipam.user.utils.user_utils import convert_host_permissions
from openipam.conf.ipam_settings import CONFIG

from netaddr.core import AddrFormatError

from braces.views import PermissionRequiredMixin, SuperuserRequiredMixin

import json
import re

User = get_user_model()


class HostListJson(PermissionRequiredMixin, BaseDatatableView):
    permission_required = 'hosts.view_host'

    order_columns = (
        'pk',
        'hostname',
        'mac',
        'addresses__address',
        'expires',
    )

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 1500

    def get_initial_queryset(self):
        qs = Host.objects.all()
        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        column_data = self.json_data.get('columns', [])

        try:

            host_search = column_data[1]['search']['value']
            mac_search = column_data[2]['search']['value']
            ip_search = column_data[3]['search']['value']
            expired_search = column_data[4]['search']['value']
            search = self.json_data.get('search_filter', '')
            is_owner = self.json_data.get('owner_filter', None)

            #group_filter = self.json_data.get('group_filter', None)
            #user_filter = self.json_data.get('user_filter', None)

            if is_owner:
                qs = qs.by_owner(self.request.user, use_groups=True)

            search_list = search.strip().split(' ') if search else []
            for search_item in search_list:
                search_str = ''.join(search_item.split(':')[1:])
                if search_item.startswith('desc:') and search_str:
                    qs = qs.filter(description__icontains=search_item[5:])
                elif search_item.startswith('user:'):
                    user = User.objects.filter(username__iexact=search_item[5:]).first()
                    if user:
                        qs = qs.by_owner(user)
                    else:
                        qs = qs.none()
                elif search_item.startswith('group:') and search_str:
                    group = Group.objects.filter(name__iexact=search_item[6:]).first()
                    if group:
                        qs = qs.by_group(group)
                    else:
                        qs = qs.none()
                elif search_item.startswith('name:') and search_str:
                    qs = qs.filter(hostname__startswith=search_item[5:].lower())
                elif search_item.startswith('mac:') and search_str:
                    mac_str = search_item[4:]
                    # Replace garbage
                    rgx = re.compile('[:,-. ]')
                    mac_str = rgx.sub('', mac_search)
                    # Split to list to put back togethor with :
                    mac_str = re.findall('..', mac_str)
                    mac_str = ':'.join(mac_str)
                    qs = qs.filter(mac__startswith=mac_str.lower())
                elif search_item.startswith('ip:') and search_str:
                    ip = search_item.split(':')[-1]
                    ip_blocks = filter(None, ip.split('.'))
                    if len(ip_blocks) < 4 or not ip_blocks[3]:
                        qs = qs.filter(
                            Q(addresses__address__startswith='.'.join(ip_blocks)) |
                            Q(leases__address__address__startswith='.'.join(ip_blocks))
                        ).distinct()
                    else:
                        qs = qs.filter(
                            Q(addresses__address=ip) |
                            Q(leases__address__address=ip)
                        ).distinct()
                elif search_item.startswith('net:') and search_str:
                    if search_item.endswith('/'):
                        qs = qs.none()
                    else:
                        qs = qs.filter(addresses__address__net_contained_or_equal=search_item[4:]).distinct()
                elif search_item:
                    like_search_term = search_item + '%'
                    cursor = connection.cursor()

                    cursor.execute('''
                        SELECT hosts.mac from hosts
                            WHERE hosts.mac::text LIKE %(lsearch)s OR hosts.hostname LIKE %(lsearch)s

                        UNION

                        SELECT addresses.mac from addresses
                            WHERE HOST(addresses.address) = %(search)s

                        UNION

                        SELECT addresses.mac from addresses
                            INNER JOIN dns_records ON addresses.address = dns_records.ip_content
                            WHERE dns_records.name LIKE %(lsearch)s

                        UNION

                        SELECT leases.mac from leases
                            WHERE HOST(leases.address) = %(search)s
                    ''', {'lsearch': like_search_term, 'search': search_item})
                    search_hosts = cursor.fetchall()
                    qs = qs.filter(mac__in=[host[0] for host in search_hosts])

            if host_search:
                if host_search.startswith('^'):
                    qs = qs.filter(hostname__startswith=host_search[1:].lower())
                elif host_search.startswith('='):
                    qs = qs.filter(hostname__exact=host_search[1:].lower())
                else:
                    qs = qs.filter(hostname__contains=host_search.lower())
            if mac_search:
                # Replace garbage
                rgx = re.compile('[:,-. ]')
                mac_str = rgx.sub('', mac_search)
                # Split to list to put back togethor with :
                mac_str = re.findall('..', mac_str)
                mac_str = ':'.join(mac_str)
                qs = qs.filter(mac__startswith=mac_str.lower())
            if ip_search:
                if '/' in ip_search and len(ip_search.split('/')) > 1:
                    if ip_search.endswith('/'):
                        qs = qs.none()
                    else:
                        qs = qs.filter(
                            Q(addresses__address__net_contained_or_equal=ip_search) |
                            Q(leases__address__address__net_contained_or_equal=ip_search, leases__ends__gt=timezone.now())
                        ).distinct()
                else:

                    ip = ip_search.split(':')[-1]
                    ip_blocks = filter(None, ip.split('.'))
                    if len(ip_blocks) < 4 or not ip_blocks[3]:
                        qs = qs.filter(
                            Q(addresses__address__startswith='.'.join(ip_blocks)) |
                            Q(leases__address__address__startswith='.'.join(ip_blocks), leases__ends__gt=timezone.now())
                        ).distinct()
                    else:
                        qs = qs.filter(
                            Q(addresses__address=ip) |
                            Q(leases__address__address=ip, leases__ends__gt=timezone.now()  )
                        ).distinct()

            # if group_filter:
            #     group = Group.objects.filter(pk=group_filter).first()
            #     if group:
            #         qs = qs.by_group(group)
            # if user_filter:
            #     user = User.objects.filter(pk=user_filter).first()
            #     if user:
            #         qs = qs.by_owner(user)

            if expired_search and expired_search == '1':
                qs = qs.filter(expires__gt=timezone.now())
            elif expired_search and expired_search == '0':
                qs = qs.filter(expires__lt=timezone.now())

        except DatabaseError:
            pass

        except AddrFormatError:
            pass

        self.qs = qs

        return qs

    def prepare_results(self, qs):
        qs_macs = [q.mac for q in qs]
        qs = Host.objects.filter(mac__in=qs_macs).extra(select={'disabled': 'hosts.mac in (select mac from disabled)'})
        value_qs = merge_values(self.ordering(qs.values('mac', 'hostname', 'expires', 'addresses__address', 'disabled',
            'leases__address', 'leases__ends', 'ip_history__stopstamp', 'mac_history__stopstamp')))

        user = self.request.user
        user_change_permissions = qs.by_change_perms(user, ids_only=True)
        global_delete_permission = user.has_perm('hosts.delete_host')
        global_change_permission = user.has_perm('hosts.change_host')

        def get_last_mac_stamp(host):
            mac_stamp = host['mac_history__stopstamp']
            if mac_stamp:
                mac_stamp = max(mac_stamp) if isinstance(mac_stamp, list) else mac_stamp
                return timezone.localtime(mac_stamp).strftime('%Y-%m-%d %I:%M %p')
            else:
                return None

        def get_last_ip_stamp(host):
            ip_stamp = host['ip_history__stopstamp']
            if ip_stamp:
                ip_stamp = max(ip_stamp) if isinstance(ip_stamp, list) else ip_stamp
                return timezone.localtime(ip_stamp).strftime('%Y-%m-%d %I:%M %p')
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
            if host['addresses__address']:
                if isinstance(host['addresses__address'], list):
                    addresses += [address for address in host['addresses__address']]
                else:
                    addresses.append(host['addresses__address'])
            if host['leases__address']:
                if not isinstance(host['leases__address'], list):
                    host['leases__address'] = [host['leases__address']]
                if not isinstance(host['leases__ends'], list):
                    host['leases__ends'] = [host['leases__ends']]

                for index, lease in enumerate(host['leases__address']):
                    try:
                        if host['leases__ends'][index] > timezone.now():
                            addresses.append(lease)
                    except IndexError:
                        pass
                #valid_leases = list(
                #    Lease.objects.filter(address__in=host['leases__address'], ends__gt=timezone.now()).values_list('address', flat=True)
                #)
                #addresses += valid_leases

            if addresses:
                #addresses = [str(address) for address in addresses]
                if len(addresses) == 1:
                    return '<span>%s</span>' % addresses[0]
                else:
                    return '''
                        <span>%s</span>
                        <span>(<a href="javascript:void(0);" title="%s">%s</a>)</span>
                    ''' % (addresses[0], '\n'.join(addresses), len(addresses))
            else:
                return '<span class="flagged">No Data</span>'

        def get_expires(expires):
            if expires < timezone.now():
                return '<span class="flagged">%s</span>' % timezone.localtime(expires).strftime('%Y-%m-%d')
            else:
                return timezone.localtime(expires).strftime('%Y-%m-%d')

        def get_selector(host, change_permissions):
            if change_permissions or global_delete_permission:
                return '<input class="action-select" name="selected_hosts" type="checkbox" value="%s" />' % host['mac']
            else:
                return ''

        def render_cell(value, is_flagged=False, is_disabled=False):
            flagged = 'flagged' if is_flagged else ''
            no_data = '<span class="%s">No Data</span>' % flagged
            return value if value else no_data

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for host in value_qs:
            if global_change_permission or host['mac'] in user_change_permissions:
                change_permissions = True
            else:
                change_permissions = False
            host_view_href = reverse_lazy('view_host', args=(slugify(host['mac']),))
            host_edit_href = reverse_lazy('update_host', args=(slugify(host['mac']),))
            host_ips = get_ips(host)
            expires = get_expires(host['expires'])
            last_mac_stamp = get_last_mac_stamp(host)
            last_ip_stamp = get_last_ip_stamp(host)

            if not host_ips:
                is_flagged = True
            else:
                is_flagged = False if last_ip_stamp or last_mac_stamp else True

            is_disabled = 'disabled' if host['disabled'] else ''

            json_data.append([
                get_selector(host, change_permissions),
                ('<a href="%(view_href)s" rel="%(hostname)s" id="%(update_href)s"'
                 ' class="host-details %(is_disabled)s" data-toggle="modal"><span class="glyphicon glyphicon-chevron-right"></span> %(hostname)s</a>' % {
                                                                                    'hostname': host['hostname'] or 'N/A',
                                                                                    'view_href': host_view_href,
                                                                                    'update_href': host_edit_href,
                                                                                    'is_disabled': is_disabled
                                                                                }),
                host['mac'],
                host_ips,
                expires,
                render_cell(last_mac_stamp, is_flagged, is_disabled),
                render_cell(last_ip_stamp, is_flagged, is_disabled),
                '<a href="%s?q=host:%s">DNS Records</a>' % (reverse_lazy('list_dns'), host['hostname']),
                '<a href="%s">%s</a>' % (
                    host_edit_href if change_permissions else host_view_href,
                    'Edit' if change_permissions else 'View'
                ),
            ])

        return json_data


class HostListView(PermissionRequiredMixin, TemplateView):
    permission_required = 'hosts.view_host'
    template_name = 'hosts/host_list.html'

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)

        owner_filter = self.request.COOKIES.get('owner_filter', None)
        context['owner_filter'] = self.request.GET.get('mine', owner_filter)
        context['search_filter'] = urlunquote(self.request.COOKIES.get('search_filter', ''))
        context['owners_form'] = HostOwnerForm()
        context['renew_form'] = HostRenewForm(user=self.request.user)

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(HostListView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        action = request.POST.get('action', None)
        selected_hosts = request.POST.getlist('selected_hosts', [])

        if selected_hosts:
            selected_hosts = Host.objects.filter(pk__in=selected_hosts)

            # If action is to change owners on host(s)
            if action == 'owners':
                assign_owner_hosts(request, selected_hosts)
            elif action == 'delete':
                delete_hosts(request, selected_hosts)
            elif action == 'renew':
                renew_hosts(request, selected_hosts)

        return redirect('list_hosts')


class HostDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'hosts.view_host'
    model = Host
    noaccess = False

    def get(self, request, *args, **kwargs):
        if CONFIG.get('CONVERT_OLD_PERMISSIONS'):
           convert_host_permissions(host_pk=self.kwargs.get('pk'), on_empty_only=True)
        return super(HostDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostDetailView, self).get_context_data(**kwargs)
        attributes = []
        attributes += self.object.freeform_attributes.values_list('attribute__description', 'value')
        attributes += self.object.structured_attributes.values_list('structured_attribute_value__attribute__description',
                                                                    'structured_attribute_value__value')
        context['read_only'] = self.kwargs.get('read_only', False)
        context['attributes'] = attributes
        context['dns_records'] = self.object.get_dns_records()
        context['addresses'] = self.object.addresses.all()
        context['pools'] = self.object.pools.all()
        context['leased_addresses'] = self.object.leases.select_related('address').all()
        context['user_owners'], context['group_owners'] = self.object.get_owners(ids_only=False)
        context['disabled_info'] = Disabled.objects.filter(host=self.object.pk).first()
        context['disabled_website'] = CONFIG.get('DISABLED_HOSTS_WEBSITE')

        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return ['hosts/inc/detail.html']
        else:
            return super(HostDetailView, self).get_template_names()

    def dispatch(self, request, *args, **kwargs):
        return super(HostDetailView, self).dispatch(request, *args, **kwargs)


class HostUpdateCreateMixin(object):
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def get_form(self, form_class):
        is_bulk = self.kwargs.get('bulk', False)
        if not is_bulk and self.request.session.get('host_form_add'):
            del self.request.session['host_form_add']

        # passing the user object to the form here.
        form = form_class(request=self.request, **self.get_form_kwargs())

        return form

    def get_context_data(self, **kwargs):
        context = super(HostUpdateCreateMixin, self).get_context_data(**kwargs)
        context['dynamic_address_types'] = json.dumps(
            [address_type.pk for address_type in AddressType.objects.filter(pool__isnull=False)]
        )
        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super(HostUpdateCreateMixin, self).post(request, *args, **kwargs)
        except ValidationError as e:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if not getattr(form, '_errors'):
                form._errors = ErrorDict()
            error_list = form._errors.setdefault(NON_FIELD_ERRORS, ErrorList())

            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)

            error_list.append('Please try again.')
            return self.form_invalid(form)


class HostUpdateView(HostUpdateCreateMixin, UpdateView):
    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        return super(HostUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostUpdateView, self).get_context_data(**kwargs)
        context['disabled_info'] = Disabled.objects.filter(host=self.object.pk).first()
        context['disabled_website'] = CONFIG.get('DISABLED_HOSTS_WEBSITE')
        return context

    def get(self, request, *args, **kwargs):
        if CONFIG['CONVERT_OLD_PERMISSIONS']:
            convert_host_permissions(host_pk=self.kwargs.get('pk'), on_empty_only=True)
        return super(HostUpdateView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        original_object = serializers.serialize('json', [self.object])
        valid_form = super(HostUpdateView, self).form_valid(form)

        LogEntry.objects.log_action(
            user_id=self.object.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_unicode(self.object),
            action_flag=CHANGE,
            change_message=original_object
        )
        messages.success(self.request, "Host %s was successfully changed." % form.cleaned_data['hostname'],)

        if self.request.POST.get('_continue'):
            return redirect(reverse_lazy('update_host', kwargs={'pk': slugify(self.object.pk)}))

        return valid_form


class HostCreateView(PermissionRequiredMixin, HostUpdateCreateMixin, CreateView):
    permission_required = 'hosts.add_host'

    def form_valid(self, form):
        valid_form = super(HostCreateView, self).form_valid(form)

        LogEntry.objects.log_action(
            user_id=self.object.user.pk,
            content_type_id=ContentType.objects.get_for_model(self.object).pk,
            object_id=self.object.pk,
            object_repr=force_unicode(self.object),
            action_flag=ADDITION
        )
        messages.success(self.request, "Host %s was successfully added." % form.cleaned_data['hostname'],)

        if self.request.POST.get('_continue'):
            return redirect(reverse_lazy('update_host', kwargs={'pk': slugify(self.object.pk)}))
        elif self.request.POST.get('_add'):
            # Get fields that would carry over
            self.request.session['host_form_add'] = form.data
            return redirect(reverse_lazy('add_hosts_bulk'))

        return valid_form


class HostAddressCreateView(SuperuserRequiredMixin, DetailView):
    model = Host
    template_name = 'hosts/host_address_form.html'

    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_static is False:
            return redirect('update_host', pk=self.object.mac_stripped)
        return super(HostAddressCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostAddressCreateView, self).get_context_data(**kwargs)
        self.host_addresses = self.object.addresses.values_list('address', flat=True)
        self.addresses = Address.objects.filter(host=self.object).exclude(arecords__name=self.object.hostname)

        addresses_data = []
        for address in self.addresses:
            name = address.arecords.filter(
                Q(dns_type__name='A') | Q(dns_type__name='AAAA')
            ).first()
            addresses_data.append({
                'ip_address': address.address,
                'name': name
            })
        context['address_data'] = addresses_data

        return context

    def post(self, request, *args, **kwargs):
        new_addresses = request.POST.getlist('new-address', [])
        new_names = request.POST.getlist('new-hostname', [])
        new_ips = request.POST.getlist('new-ip', [])
        new_networks = request.POST.getlist('new-network', [])

        host = self.object
        context = self.get_context_data(object=self.object)
        data = context['form_data'] = []
        error_list = []

        try:
            for index, address in enumerate(new_addresses):
                if new_names[index] or new_networks[index] or new_ips[index]:
                    context['form_data'].append({
                        'a_type': request.POST.get('new-type-%s' % index),
                        'hostname': new_names[index],
                        'ip_address': new_ips[index],
                        'network': new_networks[index]
                    })

            for address in data:
                with transaction.atomic():
                    added_address = host.add_ip_address(
                        user=request.user,
                        ip_address=address['ip_address'] or None,
                        network=address['network'] or None,
                        hostname=address['hostname'] or None
                    )
                messages.info(request, 'Address %s has been assigned to Host %s' % (added_address.address, host.hostname))

        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                for key, errors in e.message_dict.items():
                    for error in errors:
                        error_list.append(error)
            else:
                error_list.append(e.message)

            error_list.append('Please try again.')
            messages.error(request, mark_safe('<br />'.join(error_list)))
            return render(request, self.template_name, context)

        return redirect('add_addresses_host', pk=host.mac_stripped)


class HostAddressDeleteView(SuperuserRequiredMixin, View):

    @method_decorator(permission_change_host)
    def dispatch(self, request, *args, **kwargs):
        return super(HostAddressDeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        host = get_object_or_404(Host, pk=self.kwargs.get('pk'))
        address = request.REQUEST.get('address', None)
        if address:
            try:
                Address.objects.filter(
                    host=host,
                    address=address
                ).release()
            except AddrFormatError:
                return redirect('add_addresses_host', pk=host.mac_stripped)

            messages.info(request, 'Address %s has been removed and released.' % address)
        return redirect('add_addresses_host', pk=host.mac_stripped)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


def change_owners(request):
    form = HostOwnerForm(request.POST or None)

    if form.is_valid:
        pass

    context = {
        'form': form
    }

    return render(request, 'hosts/change_owners.html', context)
