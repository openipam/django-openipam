from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.utils.http import urlunquote
from django.utils import simplejson
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q
from django.db.utils import DatabaseError

from django_datatables_view.base_datatable_view import BaseDatatableView

from openipam.hosts.decorators import permission_owner_required
from openipam.hosts.forms import HostForm, HostListForm, HostOwnerForm, HostRenewForm
from openipam.hosts.models import Host, GulRecentArpBymac, GulRecentArpByaddress, Attribute, \
    StructuredAttributeToHost, FreeformAttributeToHost, StructuredAttributeValue
from openipam.network.models import Lease


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
        is_owner = self.request.GET.get('owner_filter', '')

        if is_owner:
            qs = Host.objects.get_hosts_owned_by_user(self.request.user)
        # Otherwise get hosts based on permissions
        else:
            qs = Host.objects.all()

        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        try:

            search = self.request.GET.get('sSearch', None)
            host_search = self.request.GET.get('sSearch_0', None)
            mac_search = self.request.GET.get('sSearch_1', None)
            ip_search = self.request.GET.get('sSearch_2', None)
            expired_search = self.request.GET.get('sSearch_3', None)
            group_filter = self.request.GET.get('group_filter', None)

            search_list = search.strip().split(' ')
            for search_item in search_list:
                if search_item.startswith('desc:'):
                    #assert False, search_item.split(':')[-1]
                    qs = qs.filter(description__icontains=search_item.split(':')[-1])
                elif search_item.startswith('user:'):
                    qs = qs.filter(user_permissions__user__username__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('name:'):
                    qs = qs.filter(hostname__startswith=search_item.split(':')[-1])
                elif search_item.startswith('mac:'):
                    mac_str = search_item.split(':')
                    mac_str.pop(0)
                    mac_str = ''.join(mac_str)
                    try:
                        mac_str = ':'.join(s.encode('hex') for s in mac_str.decode('hex'))
                    except TypeError:
                        pass
                    qs = qs.filter(mac__istartswith=mac_str)
                elif search_item.startswith('ip:'):
                    qs = qs.filter(addresses__address__istartswith=search_item.split(':')[-1])
                elif search_item.startswith('net:'):
                    qs = qs.filter(addresses__address__net_contained=search_item.split(':')[-1])
                else:
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
                    qs = qs.filter(addresses__address__icontains=ip_search)
            if group_filter:
                qs = qs.filter(group_permissions__group__pk=group_filter)

            if expired_search and expired_search == '1':
                qs = qs.filter(expires__gt=timezone.now())
            elif expired_search and expired_search == '0':
                qs = qs.filter(expires__lt=timezone.now())

        except DatabaseError:
            pass

        self.qs = qs

        return qs

    def prepare_results(self, qs):

        qs_macs = [q.mac for q in qs]
        self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
        self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')

        def get_last_mac_stamp(mac):
            filtered_list = filter(lambda x: x.mac == mac, self.gul_recent_arp_bymac)
            if filtered_list:
                return timezone.localtime(filtered_list[0].stopstamp).strftime('%Y-%m-%d %I:%M %p')
            else:
                return '<span class="expired-date">No Data</span>'

        def get_last_ip_stamp(mac):
            filtered_list = filter(lambda x: x.mac == mac, self.gul_recent_arp_byaddress)
            if filtered_list:
                return timezone.localtime(filtered_list[0].stopstamp).strftime('%Y-%m-%d %I:%M %p')
            else:
                return '<span class="expired-date">No Data</span>'

        def get_last_ip(mac):
            filtered_list = filter(lambda x: x.mac == mac, self.gul_recent_arp_byaddress)
            if filtered_list:
                return str(filtered_list[0].address)
            else:
                return 'No Data'

        def get_expires(expires):
            if expires < timezone.now():
                return '<span class="expired-date">%s</span>' % expires.strftime('%Y-%m-%d')
            else:
                return expires.strftime('%Y-%m-%d')

        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for host in qs:
            host_view_href = reverse_lazy('view_host', args=(slugify(host.mac),))
            host_edit_href = reverse_lazy('update_host', args=(slugify(host.mac),))
            json_data.append([
                '<input class="action-select" name="selected_hosts" type="checkbox" value="%s" />' % host.mac,
                ('<a href="%(view_href)s" rel="%(hostname)s" id="%(update_href)s"'
                 ' class="host-details" data-toggle="modal">%(hostname)s</a>' % {
                                                                                    'hostname': host.hostname or 'N/A',
                                                                                    'view_href': host_view_href,
                                                                                    'update_href': host_edit_href
                                                                                }),
                host.mac,
                get_last_ip(host.mac),
                get_expires(host.expires),
                get_last_mac_stamp(host.mac),
                get_last_ip_stamp(host.mac),
                '<a href="%s?mac=%s">DNS Records</a>' % (reverse_lazy('list_dns'), host.mac),
                '<a href="%s">Edit</a>' % host_edit_href,
            ])
        return json_data


class HostListView(TemplateView):
    template_name = 'hosts/host_list.html'

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)
        #context['groups'] = Group.objects.all().order_by('name')

        group_initial = self.request.COOKIES.get('group_filter', None)
        if group_initial:
            context['form'] = HostListForm(initial={'groups': group_initial})
        else:
            context['form'] = HostListForm()

        context['owner_filter'] = self.request.COOKIES.get('owner_filter', '')
        context['owners_form'] = HostOwnerForm()
        context['renew_form'] = HostRenewForm(user=self.request.user)

        data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
        if data_table_state:
            context.update(simplejson.loads(data_table_state))

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
        context['leased_addresses'] = Lease.objects.filter(mac=self.object.mac)
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

    # def get_context_data(self, **kwargs):
    #     context = super(HostUpdateCreateView, self).get_context_data(**kwargs)
    #     return context

    def form_valid(self, form):
        messages.success(self.request, "Host %s was successfully changed." % form.cleaned_data['hostname'],)
        return super(HostUpdateCreateView, self).form_valid(form)


class HostUpdateView(HostUpdateCreateView, UpdateView):
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
