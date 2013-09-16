from openipam.network.models import DhcpGroup, Network
import autocomplete_light


autocomplete_light.register(DhcpGroup,
    search_fields=['name'],
    autocomplete_js_attributes={'placeholder': 'Search DHCP Groups'},
)


class NetworkAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['network', 'name']
    autocomplete_js_attributes = {'placeholder': 'Search Networks'}
autocomplete_light.register(Network, NetworkAutocomplete)
