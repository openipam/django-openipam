from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import utc
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from openipam.core.utils.permissions import get_objects_for_owner
from openipam.hosts.forms import HostForm
from openipam.hosts.models import Host, GulRecentArpBymac, GulRecentArpByaddress
from guardian.shortcuts import get_objects_for_user, assign_perm
from guardian.mixins import PermissionRequiredMixin
from guardian.forms import BaseObjectPermissionsForm
from datetime import datetime


class HostListView(ListView):
    model = Host
    paginate_by = 50
    is_owner = False

    gul_recent_arp_bymac = []
    gul_recent_arp_byaddress = []

    def get_queryset(self):
        if self.is_owner:
            qs = get_objects_for_owner(self.request.user, 'hosts', Host)
        else:
            qs = get_objects_for_user(self.request.user, ['hosts.change_host', 'hosts.is_owner'], any_perm=True)

        search = self.request.REQUEST.get('q', '')
        if search:
            qs = qs.filter(Q(hostname__icontains=search) | Q(mac__icontains=search))

        own_hosts = self.request.REQUEST.get('owner', '')
        if own_hosts:
            qs = qs.filter()

        #qs_macs = [q.mac for q in qs]
        #self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
        #self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')

        return qs

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)

        # inject arp data and sent it to context to be added on template.
        qs_macs = [q.mac for q in context['object_list']]
        self.gul_recent_arp_bymac = GulRecentArpBymac.objects.filter(mac__in=qs_macs).order_by('-stopstamp')
        self.gul_recent_arp_byaddress = GulRecentArpByaddress.objects.filter(mac__in=qs_macs).order_by('-stopstamp')

        context['is_owner'] = self.is_owner
        context['gul_recent_arp_bymac'] = self.gul_recent_arp_bymac
        context['gul_recent_arp_byaddress'] = self.gul_recent_arp_byaddress

        return context

    # post is used by filters
    def post(self, request, *args, **kwargs):
        filter_action = request.POST.get('filter', None)
        selected_hosts = request.POST.getlist('selected_hosts', [])

        if filter_action and selected_hosts:
            if filter_action == 'delete':
                Host.objects.filter(mac_in=selected_hosts).delete()
            elif filter_action == 'owners':
                return
            #for host in selected_hosts:

        return super(self, HostListView).post(request, *args, **kwargs)


class HostUpdateView(UpdateView):
    permissions = ()
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.changed_by = self.request.user

        # Update owner permissions
        instance.remove_owners()
        if form.cleaned_data['user_owners']:
            for user in form.cleaned_data['user_owners']:
                instance.assign_owner(user)
        if form.cleaned_data['group_owners']:
            for group in form.cleaned_data['group_owners']:
                instance.assign_owner(group)

        instance.save()

        messages.success(self.request, "Host %s was successfully changed." % instance.mac,)

        return HttpResponseRedirect(self.get_success_url())

   # def get_context_data(self, **kwargs):
   #     context = super(HostUpdateView, self).get_context_data(**kwargs)
   #     context['owner_form'] =
   #     return context


class HostCreateView(CreateView):
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.changed_by = self.request.user
        instance.expires = datetime.utcnow().replace(tzinfo=utc) + form.cleaned_data['expire_days'].expiration

        if form.cleaned_data['user_owners']:
            for user in form.cleaned_data['user_owners']:
                instance.assign_owner(user)
        if form.cleaned_data['group_owners']:
            for group in form.cleaned_data['group_owners']:
                instance.assign_owner(group)

        instnace.save()

        messages.success(self.request, "Host %s was successfully added." % instance.mac,)

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


# def index(request):
#     return render(request, 'hosts/index.html', {})


# def add(request):

#     form = AddHostForm(request.POST or None)

#     if form.is_valid():
#         return redirect('hosts')

#     context = {
#         'form': form
#     }

#     return render(request, 'hosts/add.html', context)
