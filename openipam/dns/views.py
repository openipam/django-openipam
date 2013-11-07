from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.contrib import messages
from openipam.dns.models import DnsRecord, DnsType
from openipam.hosts.models import Host
from openipam.dns.forms import DNSUpdateForm, BaseDNSUpdateFormset


def dns_list_edit(request):

    search_string = request.GET.get('q', None)
    mac_string = request.GET.get('mac', None)
    page = request.GET.get('page', None)
    queryset = DnsRecord.objects.none()
    page_objects = None
    DNSUpdateFormset = modelformset_factory(DnsRecord, DNSUpdateForm, formset=BaseDNSUpdateFormset, can_delete=True, extra=0)
    host = None

    if mac_string:
        queryset = DnsRecord.objects.select_related('dns_type').filter(
            address__host__mac=mac_string
        )
        host = Host.objects.get(mac=mac_string)

    elif search_string:
        queryset = DnsRecord.objects.select_related('dns_type').filter(
            #Q(domain__name__istartswith=search_string) |
            Q(name__istartswith=search_string) |
            Q(text_content__istartswith=search_string)
        )

        paginator = Paginator(queryset, 50)
        try:
            page_objects = paginator.page(page)
        except PageNotAnInteger:
            page_objects = paginator.page(1)
        except EmptyPage:
            page_objects = paginator.page(paginator.num_pages)

        # Paginated queryset for formset
        queryset = queryset.filter(id__in=[object.id for object in page_objects])
    else:
        DNSUpdateFormset.extra = 1

    formset = DNSUpdateFormset(user=request.user, data=request.POST or None, queryset=queryset)

    if formset.is_valid():
        instances = formset.save(commit=False)
        for instance in instances:
            instance.changed_by = request.user
            instance.save()

        messages.add_message(request, messages.INFO, 'DNS Entries have been saved.')

        return redirect('%s?q=%s' % (reverse('list_dns'), search_string))

    context = {
        'host': host,
        'queryset': queryset,
        'page_objects': page_objects,
        'formset': formset,
    }

    return render(request, 'dns/dnsrecord_list.html', context)


class DNSListView(ListView):
    model = DnsRecord
    template_name = 'dns/dnsrecord_list.html'
    #paginate_by = 20

    def get_queryset(self):
        search_string = self.request.GET.get('q', None)
        if search_string:
            qs = DnsRecord.objects.select_related('dns_type').filter(
                Q(domain__name__icontains=search_string) |
                Q(name__icontains=search_string) |
                Q(text_content__icontains=search_string)
            )
        else:
            qs = None

        return qs


    def get_context_data(self, **kwargs):
        context = super(DNSListView, self).get_context_data(**kwargs)
        context['dns_types'] = DnsType.objects.exclude(min_permissions__name='NONE')

        DNSUpdateFormset = modelformset_factory(DnsRecord, DNSUpdateForm, can_delete=True)
        context['formset'] = DNSUpdateFormset(queryset=context['object_list'])

        return context


    def post(self, request, *args, **kwargs):

        assert False

        return self.get(request, *args, **kwargs)


class DNSCreateView(CreateView):

    pass




def index(request):
    return render(request, 'dns/index.html', {})
