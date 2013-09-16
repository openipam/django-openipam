from django.contrib.auth.models import User, Group, Permission
from django.conf import settings
#from openipam.user.models import User
from openipam.dns.models import Domain
from openipam.hosts.models import Host
from openipam.network.models import Network, Address, Pool
import autocomplete_light


# autocomplete_light.register(User,
#     search_fields=['username', 'first_name', 'last_name', 'email'],
#     autocomplete_js_attributes={'placeholder': 'Search Users',},
# )

class IPAMObjectsAutoComplete(autocomplete_light.AutocompleteGenericBase):
    choices = (
        Domain.objects.all(),
        Network.objects.all(),
        Pool.objects.all(),
        Host.objects.all(),
    )

    search_fields = (
        ('name',),
        ('network',),
        ('name',),
        ('hostname',),
    )

    def choice_label(self, choice):
        return '%s | %s' % (choice.__class__.__name__, choice)
autocomplete_light.register(IPAMObjectsAutoComplete)


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['username', 'first_name', 'last_name', 'email']
    autocomplete_js_attributes = {'placeholder': 'Search Users'}

    def choice_label(self, choice):
        if choice.get_full_name():
            return '%s | %s' % (choice.username, choice.get_full_name())
        else:
            return unicode(choice)
autocomplete_light.register(User, UserAutocomplete)


autocomplete_light.register(Group,
    search_fields=['name'],
    autocomplete_js_attributes={'placeholder': 'Search Groups'},
)


autocomplete_light.register(Permission,
    search_fields=['name', 'content_type__app_label', 'codename'],
    autocomplete_js_attributes={'placeholder': 'Search Permissions'},
    choices=Permission.objects.select_related().filter(content_type__app_label__in=settings.IPAM_APPS)
)


autocomplete_light.register(Address,
    search_fields=['address'],
    autocomplete_js_attributes={'placeholder': 'Search Addresses'},
)

autocomplete_light.register(Domain,
    search_fields=['name'],
    autocomplete_js_attributes={'placeholder': 'Search Domains'},
)


