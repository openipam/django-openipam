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
        'placeholder': 'Search Objects',
    }

    def choice_label(self, choice):
        return '%s | %s' % (choice.__class__.__name__, choice)
autocomplete_light.register(IPAMObjectsAutoComplete)


class IPAMSearchAutoComplete(autocomplete_light.AutocompleteGenericBase):
    choices = (
        Network.objects.all(),
        User.objects.all(),
        Group.objects.all(),
    )

    search_fields = (
        ('network',),
        ('username', '^first_name', '^last_name'),
        ('name',),
    )

    autocomplete_js_attributes = {
        'minimum_characters': 2,
        'placeholder': 'Advanced Search',
    }

    def choices_for_request(self):
        """
        Propose local results and fill the autocomplete with remote
        suggestions.
        """
        assert self.choices, 'autocomplete.choices should be a queryset list'

        q = self.request.GET.get('q', '')
        choice_q = q.split(':')[0]
        q = ''.join(q.split(':')[1:])

        if choice_q == 'net':
            self.choices = (Network.objects.all(),)
            self.search_fields = (('network',),)
        elif choice_q == 'user':
            self.choices = (User.objects.all(),)
            self.search_fields = (('username', '^first_name', '^last_name'),)
        elif choice_q == 'group':
            self.choices = (Group.objects.all(),)
            self.search_fields = (('name',),)

        request_choices = []
        querysets_left = len(self.choices)

        i = 0
        for queryset in self.choices:
            conditions = self._choices_for_request_conditions(q,
                    self.search_fields[i])

            limit = ((self.limit_choices - len(request_choices)) /
                querysets_left)
            for choice in queryset.filter(conditions)[:limit]:
                request_choices.append(choice)

            querysets_left -= 1
            i += 1

        return request_choices

    def choice_label(self, choice):
        return '%s | %s' % (choice.__class__.__name__, choice)

    def choice_value(self, choice):
        if choice.__class__.__name__ == 'User':
            return 'user:%s' % choice.username
        elif choice.__class__.__name__ == 'Group':
            return 'group:%s' % choice.name
        elif choice.__class__.__name__ == 'Network':
            return 'net:%s' % choice.network
autocomplete_light.register(IPAMSearchAutoComplete)


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^username', 'first_name', 'last_name', 'email']
    autocomplete_js_attributes = {'placeholder': 'Search Users'}

    def choice_label(self, choice):
        if choice.get_full_name():
            return '%s | %s' % (choice.username, choice.get_full_name())
        else:
            return unicode(choice)
autocomplete_light.register(User, UserAutocomplete)


class UsernameAutocomplete(UserAutocomplete):
    def choice_value(self, choice):
        return choice.username
autocomplete_light.register(User, UsernameAutocomplete)


class UserFilterAutocomplete(UserAutocomplete):
    autocomplete_js_attributes = {'placeholder': 'Filter Users'}
autocomplete_light.register(User, UserFilterAutocomplete)


class GroupnameAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choice_value(self, choice):
        return choice.name
autocomplete_light.register(Group, GroupnameAutocomplete)


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

autocomplete_light.register(ContentType,
    search_fields=['model'],
    autocomplete_js_attributes={'placeholder': 'Search Content Types'},
)

class HostFilterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^hostname']
    autocomplete_js_attributes = {'placeholder': 'Filter Hosts'}
autocomplete_light.register(Host, HostFilterAutocomplete)


# autocomplete_light.register(Domain,
#     search_fields=['name'],
#     autocomplete_js_attributes={'placeholder': 'Search Domains'},
# )


