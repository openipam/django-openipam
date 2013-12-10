from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.auth import get_user_model
from openipam.dns.models import Domain, DnsType
from openipam.hosts.models import Host
from openipam.network.models import Network, Address, Pool, DhcpGroup
from guardian.shortcuts import get_objects_for_user, assign_perm
import autocomplete_light

User = get_user_model()

# autocomplete_light.register(User,
#     search_fields=['username', 'first_name', 'last_name', 'email'],
#     autocomplete_js_attributes={'placeholder': 'Search Users',},
# )

class IPAMObjectsAutoComplete(autocomplete_light.AutocompleteGenericBase):
    choices = (
        Domain.objects.all(),
        DnsType.objects.all(),
        Network.objects.all(),
        Pool.objects.all(),
        Host.objects.all(),
    )

    search_fields = (
        ('name',),
        ('name',),
        ('network',),
        ('name',),
        ('hostname',),
    )

    autocomplete_js_attributes = {
        'minimum_characters': 1,
    }

    def choice_label(self, choice):
        return '%s | %s' % (choice.__class__.__name__, choice)
autocomplete_light.register(IPAMObjectsAutoComplete,
    autocomplete_js_attributes={'placeholder': 'Search Objects'},)


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^username', 'first_name', 'last_name', 'email']
    autocomplete_js_attributes = {'placeholder': 'Search Users'}

    def choice_label(self, choice):
        if choice.get_full_name():
            return '%s | %s' % (choice.username, choice.get_full_name())
        else:
            return unicode(choice)
autocomplete_light.register(User, UserAutocomplete)


class UserFilterAutocomplete(UserAutocomplete):
    autocomplete_js_attributes = {'placeholder': 'Filter Users'}
autocomplete_light.register(User, UserFilterAutocomplete)


class DomainAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']
    autocomplete_js_attributes = {'placeholder': 'Search Domains'}

    def choices_for_request(self):
        #choices = super(DomainAutoComplete, self).choices_for_request()

        if self.request.user.is_ipamadmin:
            choices = super(DomainAutocomplete, self).choices_for_request()
        else:
            try:
                choices = get_objects_for_user(
                    self.request.user,
                    ['dns.add_records_to_domain', 'dns.is_owner_domain', 'dns.change_domain'],
                    klass=Domain,
                    any_perm=True
                )
            except ContentType.DoesNotExist:
                return []

        # choices.filter(
        #     userobjectpermission__permission__codename='add_records_to',
        #     userobjectpermission__content_type__model='domain'
        # )
        # if not self.request.user.is_staff:
        #     choices = choices.filter(private=False)

        return choices
autocomplete_light.register(Domain, DomainAutocomplete)


class NetworkAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['network', 'name']
    autocomplete_js_attributes = {'placeholder': 'Search Networks'}
autocomplete_light.register(Network, NetworkAutocomplete)


autocomplete_light.register(DhcpGroup,
    search_fields=['name'],
    autocomplete_js_attributes={'placeholder': 'Search DHCP Groups'},
)


autocomplete_light.register(Group,
    search_fields=['name'],
    autocomplete_js_attributes={'placeholder': 'Search Groups'},
)


class GroupFilterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    autocomplete_js_attributes = {'placeholder': 'Filter Groups'}
autocomplete_light.register(Group, GroupFilterAutocomplete)


autocomplete_light.register(Permission,
    search_fields=['name', 'content_type__app_label', 'codename'],
    autocomplete_js_attributes={'placeholder': 'Search Permissions'},
    choices=Permission.objects.select_related().filter(content_type__app_label__in=settings.IPAM_APPS)
)


autocomplete_light.register(Address,
    search_fields=['address'],
    autocomplete_js_attributes={'placeholder': 'Search Addresses'},
)


autocomplete_light.register(Host,
    search_fields=['mac', 'hostname'],
    autocomplete_js_attributes={'placeholder': 'Search Hosts'},
)


class HostFilterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['mac', 'hostname']
    autocomplete_js_attributes = {'placeholder': 'Filter Hosts'}
autocomplete_light.register(Host, HostFilterAutocomplete)


# autocomplete_light.register(Domain,
#     search_fields=['name'],
#     autocomplete_js_attributes={'placeholder': 'Search Domains'},
# )


