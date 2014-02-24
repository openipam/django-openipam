from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.utils.http import urlunquote
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.db.utils import DatabaseError

from django_datatables_view.base_datatable_view import BaseDatatableView

from openipam.hosts.decorators import permission_owner_required
from openipam.hosts.forms import HostForm, HostListForm, HostOwnerForm, HostRenewForm
from openipam.hosts.models import Host, GulRecentArpBymac, GulRecentArpByaddress, Attribute, \
    StructuredAttributeToHost, FreeformAttributeToHost, StructuredAttributeValue
from openipam.network.models import Lease, AddressType, Address
from openipam.user.utils.user_utils import convert_host_permissions

from guardian.shortcuts import get_objects_for_user, get_objects_for_group

import json

User = get_user_model()


class HostListJson(BaseDatatableView):
    order_columns = (
        'pk',
        'hostname',
        'mac',
        'addresses__address',
        'expires',
    )

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 100

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # Get my hosts /hosts/mine
        is_owner = self.request.GET.get('owner_filter', None)

        if is_owner:
            qs = Host.objects.get_hosts_owned_by_user(self.request.user)
        # Otherwise get hosts based on permissions
        else:
            qs = Host.objects.all()

        #return qs.prefetch_related('addresses').all()
        return qs.prefetch_related('ip_history', 'mac_history', 'pools', 'addresses', 'leases').all()

    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        try:

            host_search = self.request.GET.get('sSearch_0', None)
            mac_search = self.request.GET.get('sSearch_1', None)
            ip_search = self.request.GET.get('sSearch_2', None)
            expired_search = self.request.GET.get('sSearch_3', None)
            search = self.request.GET.get('search_filter', None)
            group_filter = self.request.GET.get('group_filter', None)
            user_filter = self.request.GET.get('user_filter', None)

            search_list = search.strip().split(' ')
            for search_item in search_list:
                if search_item.startswith('desc:'):
                    #assert False, search_item.split(':')[-1]
                    qs = qs.filter(description__icontains=search_item.split(':')[-1])
                elif search_item.startswith('user:'):
                    user = User.objects.filter(username__iexact=search_item.split(':')[-1])
                    if user:
                        qs = get_objects_for_user(
                            user[0],
                            ['hosts.is_owner_host'],
                            klass=qs,
                        )
                    else:
                        qs = qs.none()
                elif search_item.startswith('group:'):
                    group = Group.objects.filter(name__iexact=search_item.split(':')[-1])
                    if group:
                        qs = get_objects_for_group(
                            group[0],
                            ['hosts.is_owner_host'],
                            klass=qs,
                        )
                    else:
                        qs = qs.none()
                elif search_item.startswith('name:'):
                    qs = qs.filter(hostname__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('mac:'):
                    mac_str = search_item.split(':')
                    mac_str.pop(0)
                    mac_str = ''.join(mac_str)
                    try:
                        mac_str = ':'.join(s.encode('hex') for s in mac_str.decode('hex'))
                    except TypeError:
                        pass
                    qs = qs.filter(mac__startswith=mac_str)
                elif search_item.startswith('ip:'):
                    qs = qs.filter(addresses__address__startswith=search_item.split(':')[-1])
                elif search_item.startswith('net:'):
                    qs = qs.filter(addresses__address__net_contained=search_item.split(':')[-1])
                elif search_item:
                    qs = qs.filter(hostname__icontains=search_item)

            if host_search:
                qs = qs.filter(hostname__icontains=host_search)
            if mac_search:
                if ':' not in mac_search:
                    try:
                        mac_str = ':'.join(s.encode('hex') for s in mac_search.decode('hex'))
                    except TypeError:
                        mac_str = mac_search
                else:
                    mac_str = mac_search
                qs = qs.filter(mac__icontains=mac_str)
            if ip_search:
                if '/' in ip_search:
                    qs = qs.filter(addresses__address__net_contained=ip_search)
                else:
                    qs = qs.filter(addresses__address__startswith=ip_search)
            if group_filter:
                group = Group.objects.filter(pk=group_filter)
                if group:
                    qs = get_objects_for_group(
                        group[0],
                        ['hosts.is_owner_host'],
                        klass=qs
                    )
            if user_filter:
                user = User.objects.filter(pk=user_filter)
                if user:
                    qs = get_objects_for_user(
                        user[0],
                        ['hosts.is_owner_host'],
                        klass=qs
                    )
            if expired_search and expired_search == '1':
                qs = qs.filter(expires__gt=timezone.now())
            elif expired_search and expired_search == '0':
                qs = qs.filter(expires__lt=timezone.now())

        except DatabaseError:
            pass

        self.qs = qs

        return qs

    def prepare_results(self, qs):

        #qs_macs = [q.mac for q in qs]
        #self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
        #self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
        #self.dynamic_addresses = Address.objects.filter(leases__mac__in=qs_macs)

        def get_last_mac_stamp(mac):
            macs = host.mac_history.all()
            if macs:
                return timezone.localtime(macs[0].stopstamp).strftime('%Y-%m-%d %I:%M %p')
            else:
                return None

        def get_last_ip_stamp(mac):
            ips = host.ip_history.all()
            if ips:
                return timezone.localtime(ips[0].stopstamp).strftime('%Y-%m-%d %I:%M %p')
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
            if host.is_dynamic:
                addresses = [lease.pk for lease in host.leases.all()]
            else:
                addresses = host.addresses.all()

            if addresses:
                addresses = [str(address) for address in addresses]
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
                return '<span class="flagged">%s</span>' % expires.strftime('%Y-%m-%d')
            else:
                return expires.strftime('%Y-%m-%d')

        def get_selector(host, has_permissions):
            if has_permissions:
                return '<input class="action-select" name="selected_hosts" type="checkbox" value="%s" />' % host.mac
            else:
                return ''

        def render_cell(value, is_flagged=False):
            no_data = '<span class="%s">No Data</span>' % 'flagged' if is_flagged else ''
            return value if value else no_data

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for host in qs:
            has_permissions = host.user_has_onwership(self.request.user)
            host_view_href = reverse_lazy('view_host', args=(slugify(host.mac),))
            host_edit_href = reverse_lazy('update_host', args=(slugify(host.mac),))
            host_ips = get_ips(host)
            expires = get_expires(host.expires)
            last_mac_stamp = get_last_mac_stamp(host.mac)
            last_ip_stamp = get_last_ip_stamp(host.mac)

            if not host_ips:
                is_flagged = True
            else:
                is_flagged = False if last_ip_stamp or last_mac_stamp else True

            json_data.append([
                get_selector(host, has_permissions),
                ('<a href="%(view_href)s" rel="%(hostname)s" id="%(update_href)s"'
                 ' class="host-details" data-toggle="modal">%(hostname)s</a>' % {
                                                                                    'hostname': host.hostname or 'N/A',
                                                                                    'view_href': host_view_href,
                                                                                    'update_href': host_edit_href
                                                                                }),
                host.mac,
                render_cell(host_ips, is_flagged),
                expires,
                render_cell(last_mac_stamp, is_flagged),
                render_cell(last_ip_stamp, is_flagged),
                '<a href="%s">DNS Records</a>' % reverse_lazy('list_dns', kwargs={'host': host.hostname}) if host.hostname else '',
                '<a href="%s">%s</a>' % (host_edit_href, 'Edit' if has_permissions else 'View'),
            ])
        return json_data


class HostListView(TemplateView):
    template_name = 'hosts/host_list.html'

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)

        context['owner_filter'] = self.request.COOKIES.get('owner_filter', None)
        context['search_filter'] = urlunquote(self.request.COOKIES.get('search_filter', ''))
        context['owners_form'] = HostOwnerForm()
        context['renew_form'] = HostRenewForm(user=self.request.user)

        data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
        if data_table_state:
            context.update(json.loads(data_table_state))

        return context

    def post(self, request, *args, **kwargs):

        user = request.user
        action = request.POST.get('action', None)
        selected_hosts = request.POST.getlist('selected_hosts', [])

        if selected_hosts:
            selected_hosts = Host.objects.filter(pk__in=selected_hosts)

            # If action is to change owners on host(s)
            # Only IPAM admins can do this.
            if action == 'owners':
                owner_form = HostOwnerForm(request.POST)

                if user.is_ipamadmin and owner_form.is_valid():
                    user_owners = owner_form.cleaned_data['user_owners']
                    group_owners = owner_form.cleaned_data['group_owners']

                    for host in selected_hosts:
                        # Delete user and group permissions first
                        host.remove_owners()

                        # Re-assign users
                        for user in user_owners:
                            host.assign_owner(user)

                        # Re-assign groups
                        for group in group_owners:
                            host.assign_owner(group)

                    messages.success(self.request, "Ownership for selected hosts has been updated.")

                else:
                    messages.error(self.request, "There was an error changing ownership of selected hosts. "
                                   "Please content an IPAM administrator.")

            # Actions that both IPAM admins and regular users can do.
            # We do out perm checks first
            else:
                user_perms_check = False
                if user.is_ipamadmin:
                    user_perms_check = True
                else:
                    user_perm_list = [host.user_has_onwership(user) for host in selected_hosts]
                    if set(user_perm_list) == set([True]):
                        user_perms_check = True
                    else:
                        messages.error(self.request, "You do not have permissions to perform this action on the selected hosts. "
                                       "Please content an IPAM administrator.")

                # Continue if user has perms.
                if user_perms_check:
                    # If action is to delete hosts
                    if action == 'delete':
                        # Delete hosts
                        selected_hosts.delete()
                        messages.success(self.request, "Seleted hosts have been deleted.")

                    elif action == 'renew':
                        renew_form = HostRenewForm(user=request.user, data=request.POST)

                        if renew_form.is_valid():
                            for host in selected_hosts:
                                host.set_expiration(renew_form.cleaned_data['expire_days'].expiration)
                                host.save()

                            messages.success(self.request, "Expiration for selected hosts have been updated.")

                        else:
                            messages.error(self.request, "There was an error renewing the expiration of selected hosts. "
                                   "Please content an IPAM administrator.")

        return redirect('list_hosts')


class HostDetailView(DetailView):
    model = Host
    noaccess = False

    def get(self, request, *args, **kwargs):
        convert_host_permissions(host_pk=self.kwargs.get('pk'))
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
        context['leased_addresses'] = self.object.leases.all()
        context['user_owners'], context['group_owners'] = self.object.get_owners(ids_only=False)

        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return ['hosts/inc/detail.html']
        else:
            return super(HostDetailView, self).get_template_names()

    # @method_decorator(permission_owner_required)
    # def dispatch(self, *args, **kwargs):
    #     return super(HostDetailView, self).dispatch(*args, **kwargs)


class HostUpdateCreateView(object):
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def get_form(self, form_class):
        # passing the user object to the form here.
        form = form_class(user=self.request.user, **self.get_form_kwargs())

        return form

    def get_context_data(self, **kwargs):
        context = super(HostUpdateCreateView, self).get_context_data(**kwargs)
        context['dynamic_address_types'] = json.dumps(
            [address_type.pk for address_type in AddressType.objects.filter(pool__isnull=False)]
        )
        return context

    def form_valid(self, form):
        valid_form = super(HostUpdateCreateView, self).form_valid(form)
        messages.success(self.request, "Host %s was successfully changed." % form.cleaned_data['hostname'],)

        is_continue = self.request.POST.get('_continue')
        if is_continue:
            return redirect(reverse_lazy('update_host', kwargs={'pk': slugify(self.object.pk)}))

        return valid_form


class HostUpdateView(HostUpdateCreateView, UpdateView):
    def get(self, request, *args, **kwargs):
        convert_host_permissions(host_pk=self.kwargs.get('pk'))
        return super(HostUpdateView, self).get(request, *args, **kwargs)

    @method_decorator(permission_owner_required)
    def dispatch(self, *args, **kwargs):
        return super(HostUpdateView, self).dispatch(*args, **kwargs)


class HostCreateView(HostUpdateCreateView, CreateView):
    pass


def change_owners(request):
    form = HostOwnerForm(request.POST or None)

    if form.is_valid:
        pass

    context = {
        'form': form
    }

    return render(request, 'hosts/change_owners.html', context)
