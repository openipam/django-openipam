from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.utils.http import urlunquote
from django.utils import simplejson
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.db.utils import DatabaseError
from django.http import HttpResponseRedirect
from django_datatables_view.base_datatable_view import BaseDatatableView
from openipam.hosts.forms import HostForm, HostListForm
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
    is_owner = False

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 100

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # Get my hosts /hosts/mine
        if self.is_owner:
            #qs = get_objects_for_owner(self.request.user, 'hosts', Host)
            qs = Host.objects.get_hosts_owned_by_user(self.request.user)
        # Get all hosts if we are ipam admin or super user
        elif self.request.user.is_superuser or self.request.user.is_ipamadmin:
            qs = Host.objects.select_related().all()
        # Get only the hosts that have change or is owner perms
        else:
            qs = Host.objects.get_hosts_by_user(self.request.user)
        return qs

    def filter_queryset(self, qs):
        # use request parameters to filter queryset

        try:

            # simple example:
            search = self.request.GET.get('sSearch', None)
            host_search = self.request.GET.get('sSearch_0', None)
            mac_search = self.request.GET.get('sSearch_1', None)
            ip_search = self.request.GET.get('sSearch_2', None)
            expired_search = self.request.GET.get('sSearch_3', None)
            group_filter = self.request.GET.get('group_filter', None)

            if host_search:
                qs = qs.filter(hostname__icontains=host_search)
            if search:
                qs = qs.filter(Q(hostname__icontains=search) | Q(mac__icontains=search))
            if mac_search:
                qs = qs.filter(mac__icontains=mac_search)
            if ip_search:
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
                '<a href="">DNS Records</a>',
                '<a href="%s">Edit</a>' % reverse_lazy('update_host', args=(slugify(host.mac),))
            ])
        return json_data


class HostListView(TemplateView):
    template_name = 'hosts/host_list.html'
    is_owner = False

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)
        #context['groups'] = Group.objects.all().order_by('name')
        context['is_owner'] = self.is_owner
        context['form'] = HostListForm()
        data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
        if data_table_state:
            context.update(simplejson.loads(data_table_state))

        return context




# class HostListView(ListView):
#     model = Host
#     paginate_by = 50
#     is_owner = False

#     gul_recent_arp_bymac = []
#     gul_recent_arp_byaddress = []

#     def get_queryset(self):
#         # Get my hosts /hosts/mine
#         if self.is_owner:
#             #qs = get_objects_for_owner(self.request.user, 'hosts', Host)
#             qs = Host.objects.get_hosts_owned_by_user(self.request.user)
#         # Get all hosts if we are ipam admin or super user
#         elif self.request.user.is_superuser or self.request.user.is_ipamadmin:
#             qs = Host.objects.select_related().all()
#         # Get only the hosts that have change or is owner perms
#         else:
#             qs = Host.objects.get_hosts_by_user(self.request.user)

#         search = self.request.REQUEST.get('q', '')
#         if search:
#             qs = qs.filter(Q(hostname__icontains=search) | Q(mac__icontains=search))

#         own_hosts = self.request.REQUEST.get('owner', '')
#         if own_hosts:
#             qs = qs.filter()

#         #qs_macs = [q.mac for q in qs]
#         #self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
#         #self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')

#         return qs

#     def get_context_data(self, **kwargs):
#         context = super(HostListView, self).get_context_data(**kwargs)

#         # inject arp data and sent it to context to be added on template.
#         qs_macs = [q.mac for q in context['object_list']]
#         self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
#         self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')

#         context['is_owner'] = self.is_owner
#         context['gul_recent_arp_bymac'] = self.gul_recent_arp_bymac
#         context['gul_recent_arp_byaddress'] = self.gul_recent_arp_byaddress

#         data_table_state = urlunquote(self.request.COOKIES.get('SpryMedia_DataTables_result_list_', ''))
#         if data_table_state:
#             context.update(simplejson.loads(data_table_state))

#         return context

#     # post is used by filters
#     def post(self, request, *args, **kwargs):
#         filter_action = request.POST.get('filter', None)
#         selected_hosts = request.POST.getlist('selected_hosts', [])

#         if filter_action and selected_hosts:
#             if filter_action == 'delete':
#                 Host.objects.filter(mac_in=selected_hosts).delete()
#             elif filter_action == 'owners':
#                 return
#             #for host in selected_hosts:

#         return super(self, HostListView).post(request, *args, **kwargs)


class HostDetailView(DetailView):
    model = Host

    def get_context_data(self, **kwargs):
        context = super(HostDetailView, self).get_context_data(**kwargs)
        attributes = []
        attributes += self.object.freeform_attributes.values_list('attribute__description', 'value')
        attributes += self.object.structured_attributes.values_list('structured_attribute_value__attribute__description',
                                                                    'structured_attribute_value__value')
        context['attributes'] = attributes
        context['dns_records'] = self.object.dns_records()
        context['addresses'] = self.object.addresses.all()
        context['pools'] = self.object.pools.all()
        context['leased_addresses'] = Lease.objects.filter(mac=self.object.mac)
        context['user_owners'] = self.object.user_permissions.select_related().all()
        context['group_owners'] = self.object.group_permissions.select_related().all()

        return context


class HostUpdateView(UpdateView):
    permissions = ()
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def get_form(self, form_class):
        # passing the user object to the form here.
        form = form_class(user=self.request.user, **self.get_form_kwargs())

        return form

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.changed_by = self.request.user
        instance.save()

        # Update owner permissions only if super user or ipam admin
        if self.request.user.is_superuser or self.request.user.is_ipamadmin:
            instance.remove_owners()
            if form.cleaned_data['user_owners']:
                for user in form.cleaned_data['user_owners']:
                    instance.assign_owner(user)
            if form.cleaned_data['group_owners']:
                for group in form.cleaned_data['group_owners']:
                    instance.assign_owner(group)

        change_freeform_attributes(self.request.user, instance, form)

        messages.success(self.request, "Host %s was successfully changed." % instance.hostname,)

        return HttpResponseRedirect(self.get_success_url())

   # def get_context_data(self, **kwargs):
   #     context = super(HostUpdateView, self).get_context_data(**kwargs)
   #     context['owner_form'] =
   #     return context


class HostCreateView(CreateView):
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def get_form(self, form_class):
        # passing the user object to the form here.
        form = form_class(user=self.request.user, **self.get_form_kwargs())

        return form

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.changed_by = self.request.user
        instance.expires = timezone.now() + form.cleaned_data['expire_days'].expiration
        instance.save()

        if form.cleaned_data['user_owners']:
            for user in form.cleaned_data['user_owners']:
                instance.assign_owner(user)
        if form.cleaned_data['group_owners']:
            for group in form.cleaned_data['group_owners']:
                instance.assign_owner(group)

        change_freeform_attributes(self.request.user, instance, form)

        messages.success(self.request, "Host %s was successfully added." % instance.hostname,)

        return HttpResponseRedirect(self.get_success_url())

        #return super(HostCreateView, self).form_valid(form)


def change_owners(request):
    form = ChangeOwnerForm(request.POST or None)

    if form.is_valid:
        pass

    context = {
        'form': form
    }

    return render(request, 'hosts/change_owners.html', context)


def change_freeform_attributes(user, instance, form):

    # get all possible attributes
    attribute_fields = Attribute.objects.all()

    # delete all attributes so we can start over.
    instance.freeform_attributes.all().delete()
    instance.structured_attributes.all().delete()

    # get all structure attribute values for performance
    structured_attributes = StructuredAttributeValue.objects.all()

    # loop through potential values and add them
    for attribute in attribute_fields:
        attribute_name = slugify(attribute.name)
        data = form.cleaned_data.get(attribute_name, '')
        if data:
            if attribute.structured:
                attribute_value = filter(lambda x: x == data, structured_attributes)
                if attribute_value:
                    StructuredAttributeToHost.objects.create(
                        mac=instance,
                        avid=attribute_value[0],
                        changed_by=user
                    )
            else:
                FreeformAttributeToHost.objects.create(
                    mac=instance,
                    aid=attribute,
                    value=data,
                    changed_by=user
                )
    return
