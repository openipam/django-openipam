from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.core.urlresolvers import reverse_lazy
from openipam.core.utils.permissions import get_objects_for_owner
from openipam.hosts.forms import HostForm
from openipam.hosts.models import Host
from guardian.shortcuts import get_objects_for_user
from guardian.mixins import PermissionRequiredMixin


class HostListView(ListView):
    model = Host
    paginate_by = 50
    is_owner = False

    def get_queryset(self):
        if self.is_owner:
            qs = get_objects_for_owner(self.request.user, 'hosts', Host)
        else:
            qs = get_objects_for_user(self.request.user, ['hosts.change_host', 'hosts.is_owner'], any_perm=True)

        search = self.request.REQUEST.get('q', '')
        if search:
            qs = qs.filter(hostname__icontains=search)

        own_hosts = self.request.REQUEST.get('owner', '')
        if own_hosts:
            qs = qs.filter()

        return qs

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)
        context['is_owner'] = self.is_owner
        return context


    # def get(self, request, *args, **kwargs):
    #     search = request.GET.get('q', '')
    #     if search:
    #         self.queryset.filter(mac__icontains=search)

    #     return super(self, HostListView).get(request, *args, **kwargs)


class HostUpdateView(UpdateView):
    permissions = ()
    model = Host
    form_class = HostForm
    success_url = reverse_lazy('list_hosts')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.changed_by = self.request.user
        super(HostUpdateView, self).save(form)


class HostCreateView(CreateView):
    model = Host
    form_class = HostForm


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
