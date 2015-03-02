from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from openipam.conf.ipam_settings import CONFIG
from openipam.dns.models import Domain, DnsType
from openipam.hosts.models import Host
from openipam.network.models import Network, Address, AddressType, Pool, DhcpGroup
from openipam.user.models import Group as OldGroup

from taggit.models import Tag

from guardian.shortcuts import get_objects_for_user, assign_perm

import autocomplete_light

User = get_user_model()

# autocomplete_light.register(User,
#     search_fields=['username', 'first_name', 'last_name', 'email'],
#     attrs={'placeholder': 'Search Users',},
# )

class IPAMObjectsAutoComplete(autocomplete_light.AutocompleteGenericBase):
    choices = (
        Domain.objects.all(),
        Network.objects.all(),
        Pool.objects.all(),
        DnsType.objects.all(),
        Host.objects.all(),
    )

    search_fields = (
        ('^name',),
        ('^network',),
        ('name',),
        ('name',),
        ('^hostname',),
    )

    attrs = {
        'minimum_characters': 1,
        'placeholder': 'Search Objects',
    }

    #WTF?
    def choices_for_request(self):
        """
        Return a list of choices from every queryset in :py:attr:`choices`.
        """
        assert self.choices, 'autocomplete.choices should be a queryset list'

        q = self.request.GET.get('q', '')

        request_choices = []
        querysets_left = len(self.choices)

        i = 0

        for queryset in self.choices:
            conditions = self._choices_for_request_conditions(q, self.search_fields[i])

            for choice in queryset.filter(conditions)[:self.limit_choices]:
                request_choices.append(choice)

            querysets_left -= 1
            i += 1

        return request_choices

    def choice_label(self, choice):
        return '%s | %s' % (choice.__class__.__name__, choice)
autocomplete_light.register(IPAMObjectsAutoComplete)


class IPAMSearchAutoComplete(autocomplete_light.AutocompleteGenericBase):
    split_words = True

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

    attrs = {
        'minimum_characters': 2,
        'placeholder': 'Advanced Search',
    }

    def choices_for_request(self):
        """
        Propose local results and fill the autocomplete with remote
        suggestions.
        """
        assert self.choices, 'autocomplete.choices should be a queryset list'

        q = self.request.GET.get('q', '').split(',')[-1]
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
        if choice.__class__.__name__ == 'User':
            return '%s | %s | %s' % (choice.__class__.__name__, choice, choice.get_full_name())
        else:
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
    search_fields = ['^username', '^first_name', '^last_name', 'email']
    attrs = {'placeholder': 'Search Users'}
    split_words = True

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
    attrs = {'placeholder': 'Filter Users'}
autocomplete_light.register(User, UserFilterAutocomplete)


class GroupnameAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']

    def choice_value(self, choice):
        return choice.name
autocomplete_light.register(Group, GroupnameAutocomplete)


class DomainAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {'placeholder': 'Search Domains'}
    limit_choices = 10

    def __init__(self, *args, **kwargs):
        super(DomainAutocomplete, self).__init__(*args, **kwargs)

        if not self.request.user.is_ipamadmin:
            self.choices = get_objects_for_user(
                self.request.user,
                ['dns.add_records_to_domain', 'dns.is_owner_domain', 'dns.change_domain'],
                klass=Domain,
                any_perm=True,
            )
autocomplete_light.register(Domain, DomainAutocomplete)


class NetworkAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['network', 'name', 'tags__name']
    attrs = {'placeholder': 'Search Networks'}

    def choices_for_request(self):
        atype = self.request.GET.get('atype')
        if atype:
            address_type = AddressType.objects.filter(id=atype).first()
            if address_type:
                self.choices = self.choices.by_address_type(address_type)

        return super(NetworkAutocomplete, self).choices_for_request()

autocomplete_light.register(Network, NetworkAutocomplete)


autocomplete_light.register(DhcpGroup,
    search_fields=['name'],
    attrs={'placeholder': 'Search DHCP Groups'},
    limit_choices=100,
)


autocomplete_light.register(Group,
    search_fields=['name'],
    attrs={'placeholder': 'Search Groups'},
)

class OldGroupAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'Search Groups'}
autocomplete_light.register(OldGroup, OldGroupAutocomplete)


class GroupFilterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'Filter Groups'}
autocomplete_light.register(Group, GroupFilterAutocomplete)


autocomplete_light.register(Permission,
    split_words=True,
    search_fields=['name', 'content_type__app_label', 'codename'],
    attrs={'placeholder': 'Search Permissions'},
    choices=Permission.objects.select_related().filter(content_type__app_label__in=CONFIG['APPS'])
)

class AddressAvailableAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^address']
    attrs = {'placeholder': 'Search Networks'}

    def __init__(self, *args, **kwargs):
        super(AddressAvailableAutocomplete, self).__init__(*args, **kwargs)

        user_pools = get_objects_for_user(
            self.request.user,
            ['network.add_records_to_pool', 'network.change_pool'],
            any_perm=True
        )
        user_nets = get_objects_for_user(
            self.request.user,
            ['network.add_records_to_network', 'network.is_owner_network', 'network.change_network'],
            any_perm=True
        )

        self.choices = Address.objects.filter(
            Q(pool__in=user_pools) | Q(pool__isnull=True),
            Q(leases__isnull=True) | Q(leases__abandoned=True) | Q(leases__ends__lte=timezone.now()),
            network__in=user_nets
            host__isnull=True,
            reserved=False
        )
autocomplete_light.register(Address, AddressAvailableAutocomplete)

autocomplete_light.register(Address,
    search_fields=['address'],
    attrs={'placeholder': 'Search Addresses'},
)

autocomplete_light.register(Host,
    search_fields=['mac', 'hostname'],
    attrs={'placeholder': 'Search Hosts'},
)

autocomplete_light.register(Permission,
    search_fields=['name', 'codename', 'content_type__name', 'content_type__app_label'],
    attrs={'placeholder': 'Search Permissions'},
)

autocomplete_light.register(ContentType,
    search_fields=['model'],
    attrs={'placeholder': 'Search Content Types'},
)

class HostFilterAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^hostname']
    attrs = {'placeholder': 'Filter Hosts'}
autocomplete_light.register(Host, HostFilterAutocomplete)


# autocomplete_light.register(Domain,
#     search_fields=['name'],
#     attrs={'placeholder': 'Search Domains'},
# )

autocomplete_light.register(Tag,
    attrs = {'placeholder': 'Search Tags'}
)
