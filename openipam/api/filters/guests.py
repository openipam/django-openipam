from django_filters import FilterSet, CharFilter

from openipam.hosts.models import GuestTicket


class GuestTicketFilter(FilterSet):
    user = CharFilter(name='user__username', lookup_expr='iexact')

    class Meta:
        model = GuestTicket
        fields = ('starts', 'ends', 'user', 'ticket',)
