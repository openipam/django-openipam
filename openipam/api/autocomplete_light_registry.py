#from django.contrib.auth.models import Group, Permission
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.auth import get_user_model
#from django.db.models import Q
#from django.utils import timezone
#
#from openipam.conf.ipam_settings import CONFIG
#from openipam.dns.models import Domain, DnsType
#from openipam.hosts.models import (
#    Host,
#    StructuredAttributeValue,
#    FreeformAttributeToHost,
#)
#from openipam.network.models import (
#    Network,
#    Address,
#    AddressType,
#    Pool,
#    DhcpGroup,
#    Building,
#)
#
#from taggit.models import Tag
#
#from guardian.shortcuts import get_objects_for_user
#from guardian.models import GroupObjectPermission, UserObjectPermission
#
#from autocomplete_light import shortcuts as al
#
#import six
#
#User = get_user_model()
#
## autocomplete_light.register(User,
##     search_fields=['username', 'first_name', 'last_name', 'email'],
##     attrs={'placeholder': 'Search Users',},
## )
#
#
#class BugAutocompleteFix(object):
#    def order_choices(self, choices):
#        """
#        Order choices using :py:attr:`order_by` option if it is set.
#        """
#        if isinstance(self.order_by, six.string_types):
#            self.order_by = (self.order_by,)
#
#        if self.values:
#            pk_name = self.model._meta.pk.name
#            try:
#                if len(choices) > 0:
#                    pk_name = choices[0]._meta.pk.name
#            except Exception:
#                pass
#
#            # Order in the user selection order when self.values is set.
#            clauses = " ".join(
#                [
#                    "WHEN %s='%s' THEN %s" % (pk_name, pk, i)
#                    for i, pk in enumerate(self.values)
#                ]
#            )
#            ordering = "CASE %s END" % clauses
#
#            _order_by = ("ordering",)
#            if self.order_by:
#                _order_by += self.order_by
#
#            return choices.extra(select={"ordering": ordering}, order_by=_order_by)
#
#        if self.order_by is None:
#            return choices
#
#        return choices.order_by(*self.order_by)
#
#
## class IPAMObjectsAutoComplete(al.AutocompleteGenericBase):
##     choices = (
##         Domain.objects.all(),
##         Pool.objects.all(),
##         DnsType.objects.all(),
##         Host.objects.all(),
##         Network.objects.all(),
##     )
## 
##     search_fields = (("^name",), ("name",), ("name",), ("^hostname",), ("^network",))
## 
##     attrs = {"minimum_characters": 1, "placeholder": "Search Objects"}
## 
##     # Override this function until it is fixed for 1.8
##     def choices_for_values(self):
##         values_choices = []
## 
##         for queryset in self.choices:
##             ctype = ContentType.objects.get_for_model(queryset.model).pk
## 
##             try:
## 
##                 ids = [
##                     x.split("-")[1]
##                     for x in self.values
##                     if x is not None and int(x.split("-")[0]) == ctype
##                 ]
##             except ValueError:
##                 continue
## 
##             # Bug?
##             if ids:
##                 for choice in queryset.filter(pk__in=ids):
##                     values_choices.append(choice)
## 
##         return values_choices
## 
##     # WTF?
##     def choices_for_request(self):
##         """
##         Return a list of choices from every queryset in :py:attr:`choices`.
##         """
##         assert self.choices, "autocomplete.choices should be a queryset list"
## 
##         q = self.request.GET.get("q", "")
## 
##         request_choices = []
##         querysets_left = len(self.choices)
## 
##         i = 0
## 
##         for queryset in self.choices:
##             conditions = self._choices_for_request_conditions(q, self.search_fields[i])
## 
##             for choice in queryset.filter(conditions)[: self.limit_choices]:
##                 request_choices.append(choice)
## 
##             querysets_left -= 1
##             i += 1
## 
##         return request_choices
## 
##     def choice_label(self, choice):
##         return "%s | %s" % (choice.__class__.__name__, choice)
## 
## 
## al.register(IPAMObjectsAutoComplete)
## 
## 
## class IPAMSearchAutoComplete(al.AutocompleteGenericBase):
##     split_words = True
## 
##     choices = (
##         Network.objects.all(),
##         User.objects.all(),
##         Group.objects.all(),
##         StructuredAttributeValue.objects.all(),
##         FreeformAttributeToHost.objects.all(),
##         AddressType.objects.all(),
##     )
## 
##     search_fields = (
##         ("network", "name"),
##         ("username", "^first_name", "^last_name"),
##         ("^name",),
##         ("attribute__name", "value"),
##         ("attribute__name", "value"),
##         ("name", "description"),
##     )
## 
##     attrs = {"minimum_characters": 2, "placeholder": "Advanced Search"}
## 
##     # def choices_for_request(self):
##     #     """
##     #     Propose local results and fill the autocomplete with remote
##     #     suggestions.
##     #     """
##     #     assert self.choices, 'autocomplete.choices should be a queryset list'
## 
##     #     q = self.request.GET.get('q', '').split(',')[-1]
##     #     choice_q = q.split(':')[0]
##     #     q = ''.join(q.split(':')[1:])
## 
##     #     if choice_q == 'net':
##     #         self.choices = (Network.objects.all(),)
##     #         self.search_fields = (('network',),)
##     #     elif choice_q == 'user':
##     #         self.choices = (User.objects.all(),)
##     #         self.search_fields = (('username', '^first_name', '^last_name'),)
##     #     elif choice_q == 'group':
##     #         self.choices = (Group.objects.all(),)
##     #         self.search_fields = (('name',),)
## 
##     #     request_choices = []
##     #     querysets_left = len(self.choices)
## 
##     #     i = 0
##     #     for queryset in self.choices:
##     #         conditions = self._choices_for_request_conditions(q,
##     #                 self.search_fields[i])
## 
##     #         limit = ((self.limit_choices - len(request_choices)) /
##     #             querysets_left)
##     #         for choice in queryset.filter(conditions)[:limit]:
##     #             request_choices.append(choice)
## 
##     #         querysets_left -= 1
##     #         i += 1
## 
##     #     return request_choices
## 
##     def choice_label(self, choice):
##         if choice.__class__.__name__ == "User":
##             return "%s | %s | %s" % (
##                 choice.__class__.__name__,
##                 choice,
##                 choice.get_full_name(),
##             )
##         elif choice.__class__.__name__ in [
##             "StructuredAttributeValue",
##             "FreeformAttributeToHost",
##         ]:
##             return "%s | %s | %s" % ("Attribute", choice.attribute, choice.value)
##         elif choice.__class__.__name__ == "AddressType":
##             return "%s | %s" % ("Address Type", choice)
##         elif choice.__class__.__name__ == "Network":
##             return "%s | %s | %s" % ("Network", choice.name, choice)
##         else:
##             return "%s | %s" % (choice.__class__.__name__, choice)
## 
##     def choice_value(self, choice):
##         if choice.__class__.__name__ == "User":
##             return "user:%s" % choice.username
##         elif choice.__class__.__name__ == "Group":
##             return "group:%s" % choice.name
##         elif choice.__class__.__name__ == "Network":
##             return "net:%s" % choice.network
##         elif choice.__class__.__name__ == "StructuredAttributeValue":
##             return "sattr:%s" % choice.value
##         elif choice.__class__.__name__ == "FreeformAttributeToHost":
##             return "fattr:%s" % choice.value
##         elif choice.__class__.__name__ == "AddressType":
##             return "atype:%s" % choice.pk
## 
## 
## al.register(IPAMSearchAutoComplete)
## 
## 
## class IPAMUserSearchAutoComplete(al.AutocompleteGenericBase):
##     split_words = True
## 
##     choices = (
##         User.objects.all(),
##         Group.objects.filter(user__isnull=False),
##         GroupObjectPermission.objects.all(),
##         UserObjectPermission.objects.all(),
##     )
## 
##     search_fields = (
##         ("username", "^first_name", "^last_name", "email"),
##         ("^name",),
##         ("object_pk", "permission__name", "permission__codename"),
##         ("object_pk", "permission__name", "permission__codename"),
##     )
## 
##     attrs = {"minimum_characters": 2, "placeholder": "Advanced Search"}
## 
##     def choices_for_request(self):
##         """
##         Propose local results and fill the autocomplete with remote
##         suggestions.
##         """
##         assert self.choices, "autocomplete.choices should be a queryset list"
## 
##         q = self.request.GET.get("q", "").split(",")[-1]
##         choice_q = q.split(":")[0]
##         q = "".join(q.split(":")[1:])
## 
##         self.choices = []
##         self.search_fields = []
## 
##         if q:
##             if choice_q == "user":
##                 self.choices = (User.objects.all(),)
##                 self.search_fields = (
##                     ("username", "^first_name", "^last_name", "email"),
##                 )
##             elif choice_q == "group":
##                 self.choices = (Group.objects.all(),)
##                 self.search_fields = (("^name",),)
##             elif choice_q == "perm":
##                 self.choices = (
##                     GroupObjectPermission.objects.filter(
##                         Q(
##                             object_pk__in=[
##                                 host.pk
##                                 for host in Host.objects.filter(
##                                     hostname__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 network.pk
##                                 for network in Network.objects.filter(
##                                     network__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 domain.pk
##                                 for domain in Domain.objects.filter(
##                                     name__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 pool.pk
##                                 for pool in Pool.objects.filter(name__istartswith=q)[
##                                     :10
##                                 ]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 dnstype.pk
##                                 for dnstype in DnsType.objects.filter(
##                                     name__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                     ),
##                     UserObjectPermission.objects.filter(
##                         Q(
##                             object_pk__in=[
##                                 host.pk
##                                 for host in Host.objects.filter(
##                                     hostname__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 network.pk
##                                 for network in Network.objects.filter(
##                                     network__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 domain.pk
##                                 for domain in Domain.objects.filter(
##                                     name__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 pool.pk
##                                 for pool in Pool.objects.filter(name__istartswith=q)[
##                                     :10
##                                 ]
##                             ]
##                         )
##                         | Q(
##                             object_pk__in=[
##                                 dnstype.pk
##                                 for dnstype in DnsType.objects.filter(
##                                     name__istartswith=q
##                                 )[:10]
##                             ]
##                         )
##                     ),
##                 )
##                 self.search_fields = ([], [])
## 
##         request_choices = []
##         querysets_left = len(self.choices)
## 
##         i = 0
##         for queryset in self.choices:
##             conditions = self._choices_for_request_conditions(q, self.search_fields[i])
## 
##             limit = (self.limit_choices - len(request_choices)) / querysets_left
##             for choice in queryset.filter(conditions)[:limit]:
##                 request_choices.append(choice)
## 
##             querysets_left -= 1
##             i += 1
## 
##         return request_choices
## 
##     def choice_label(self, choice):
##         if choice.__class__.__name__ == "User":
##             return "%s | %s | %s" % (
##                 choice.__class__.__name__,
##                 choice,
##                 choice.get_full_name(),
##             )
##         else:
##             return "%s | %s" % (choice.__class__.__name__, choice)
## 
##     def choice_value(self, choice):
##         if choice.__class__.__name__ == "User":
##             return "user:%s" % choice.username
##         elif choice.__class__.__name__ == "Group":
##             return "group:%s" % choice.name
##         elif choice.__class__.__name__ == "GroupObjectPermission":
##             return "gperm:%s" % choice.pk
##         elif choice.__class__.__name__ == "UserObjectPermission":
##             return "uperm:%s" % choice.pk
## 
## 
## al.register(IPAMUserSearchAutoComplete)
## 
## 
## class UserAutocomplete(al.AutocompleteModelBase):
##     search_fields = ["^username", "^first_name", "^last_name", "email"]
##     attrs = {"placeholder": "Search Users"}
##     split_words = True
## 
##     def choice_label(self, choice):
##         if choice.get_full_name():
##             return "%s | %s" % (choice.username, choice.get_full_name())
##         else:
##             return str(choice)
## 
## 
## al.register(User, UserAutocomplete)
## 
## 
## class UsernameAutocomplete(UserAutocomplete):
##     def choice_value(self, choice):
##         return choice.username
## 
## 
## al.register(User, UsernameAutocomplete)
## 
## 
## class UserFilterAutocomplete(UserAutocomplete):
##     attrs = {"placeholder": "Filter Users"}
## 
## 
## al.register(User, UserFilterAutocomplete)
## 
## 
## class GroupnameAutocomplete(al.AutocompleteModelBase):
##     search_fields = ["name"]
## 
##     def choice_value(self, choice):
##         return choice.name
## 
## 
## al.register(Group, GroupnameAutocomplete)
## 
## 
## class DomainAutocomplete(al.AutocompleteModelBase):
##     search_fields = ["^name"]
##     attrs = {"placeholder": "Search Domains"}
##     limit_choices = 10
## 
##     def choices_for_request(self):
##         if not self.request.user.is_anonymous() and not self.request.user.is_ipamadmin:
##             self.choices = get_objects_for_user(
##                 self.request.user,
##                 [
##                     "dns.add_records_to_domain",
##                     "dns.is_owner_domain",
##                     "dns.change_domain",
##                 ],
##                 klass=Domain,
##                 any_perm=True,
##             )
##         return super(DomainAutocomplete, self).choices_for_request()
## 
## 
## al.register(Domain, DomainAutocomplete)
## 
## 
## class NetworkAutocomplete(BugAutocompleteFix, al.AutocompleteModelBase):
##     search_fields = ["network", "name", "tags__name"]
##     attrs = {"placeholder": "Search Networks"}
## 
##     def choices_for_request(self):
##         atype = self.request.GET.get("atype")
##         if atype:
##             address_type = AddressType.objects.filter(id=atype).first()
##             if address_type:
##                 self.choices = self.choices.by_address_type(address_type)
## 
##         return super(NetworkAutocomplete, self).choices_for_request()
## 
## 
## al.register(Network, NetworkAutocomplete)
## 
## 
## al.register(
##     DhcpGroup,
##     search_fields=["name"],
##     attrs={"placeholder": "Search DHCP Groups"},
##     limit_choices=100,
## )
## 
## 
## al.register(Group, search_fields=["name"], attrs={"placeholder": "Search Groups"})
## 
## 
## al.register(Building, search_fields=["name", "number", "abbreviation"])
## 
## 
## class GroupFilterAutocomplete(al.AutocompleteModelBase):
##     search_fields = ["name"]
##     attrs = {"placeholder": "Filter Groups"}
## 
## 
## al.register(Group, GroupFilterAutocomplete)
## 
## 
## al.register(
##     Permission,
##     split_words=True,
##     search_fields=["name", "content_type__app_label", "codename"],
##     attrs={"placeholder": "Search Permissions"},
##     choices=Permission.objects.select_related().filter(
##         content_type__app_label__in=CONFIG["APPS"]
##     ),
## )
## 
## 
## class AddressAvailableAutocomplete(BugAutocompleteFix, al.AutocompleteModelBase):
##     search_fields = ["^address"]
##     attrs = {"placeholder": "Search Addresses"}
## 
##     def choices_for_request(self):
##         user_pools = get_objects_for_user(
##             self.request.user,
##             ["network.add_records_to_pool", "network.change_pool"],
##             any_perm=True,
##         )
##         user_nets = get_objects_for_user(
##             self.request.user,
##             [
##                 "network.add_records_to_network",
##                 "network.is_owner_network",
##                 "network.change_network",
##             ],
##             any_perm=True,
##         )
##         self.choices = Address.objects.filter(
##             Q(pool__in=user_pools) | Q(pool__isnull=True),
##             Q(leases__isnull=True)
##             | Q(leases__abandoned=True)
##             | Q(leases__ends__lte=timezone.now()),
##             network__in=user_nets,
##             host__isnull=True,
##             reserved=False,
##         )
##         return super(AddressAvailableAutocomplete, self).choices_for_request()
## 
## 
## al.register(Address, AddressAvailableAutocomplete)
## 
## 
## class AddressAutocomplete(BugAutocompleteFix, al.AutocompleteModelBase):
##     search_fields = ["address"]
##     attrs = {"placeholder": "Search Addresses"}
## 
## 
## al.register(Address, AddressAutocomplete)
## 
## 
## al.register(
##     Permission,
##     search_fields=["name", "codename", "content_type__app_label"],
##     attrs={"placeholder": "Search Permissions"},
## )
## 
## al.register(
##     ContentType, search_fields=["model"], attrs={"placeholder": "Search Content Types"}
## )
## 
## 
## class HostAutocomplete(BugAutocompleteFix, al.AutocompleteModelBase):
##     search_fields = ["mac", "hostname"]
##     attrs = {"placeholder": "Search Hosts"}
## 
## 
## al.register(Host, HostAutocomplete)
## 
## 
## class HostFilterAutocomplete(BugAutocompleteFix, al.AutocompleteModelBase):
##     search_fields = ["^hostname"]
##     attrs = {"placeholder": "Filter Hosts"}
## 
## 
## al.register(Host, HostFilterAutocomplete)
## 
## 
## # al.register(Domain,
## #     search_fields=['name'],
## #     attrs={'placeholder': 'Search Domains'},
## # )
## 
## al.register(Tag, attrs={"placeholder": "Search Tags"})
#