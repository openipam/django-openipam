from django_filters import FilterSet, CharFilter
from openipam.network.models import Network, Address
from taggit.forms import TagField


class TagFilter(CharFilter):
    field_class = TagField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("lookup_expr", "in")
        super().__init__(*args, **kwargs)


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_expr="net_contains_or_equals")
    name = CharFilter(lookup_expr="icontains")
    tags = TagFilter(field_name="tags__slug")

    class Meta:
        model = Network
        fields = ["name", "shared_network", "tags"]


class AddressFilter(FilterSet):
    address = CharFilter(lookup_expr="net_contains_or_equals")
    mac = CharFilter(lookup_expr="net_contains_or_equals")

    class Meta:
        model = Address
        fields = ["address", "mac"]
