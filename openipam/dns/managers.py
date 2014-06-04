from django.db.models import Model, Manager, Q
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from openipam.hosts.models import Host
from openipam.network.models import Address

from guardian.shortcuts import get_objects_for_user

from netaddr.core import AddrFormatError

import operator

User = get_user_model()



class DomainMixin(object):
    def by_owner(self, user, use_groups=False, ids_only=False, names_only=False):
        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)
        perm_user.is_superuser = False

        domains = get_objects_for_user(perm_user, 'dns.is_owner_domain', use_groups=use_groups)

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        if ids_only:
            domain_names = [domain.pk for domain in domains]
            return tuple(domains)
        else:
            return domains

    def by_change_perms(self, user, pk=None, ids_only=False, names_only=False):
        if user.has_perm('dns.change_domain') or user.has_perm('dns.is_owner_domain'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            domain_perms = get_objects_for_user(
                user,
                ['dns.is_owner_domain', 'dns.change_domain'],
                any_perm=True
            ).values_list('name', flat=True)

            qs = self.filter(name__in=list(domain_perms))

            if pk:
                qs = qs.filter(pk=pk).first()

            if names_only:
                return tuple([domain.name for domain in qs])

            if ids_only:
                return tuple([domain.pk for domain in qs])
            else:
                return qs

    def by_dns_change_perms(self, user, pk=None):
        if user.has_perm('dns.change_domain') or user.has_perm('dns.is_owner_domain'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            domain_perms = get_objects_for_user(
                user,
                ['dns.is_owner_domain', 'dns.add_records_to_domain', 'dns.change_domain'],
                any_perm=True
            ).values_list('name', flat=True)

            qs = self.filter(name__in=list(domain_perms))

            if pk:
                qs = qs.filter(pk=pk).first()

            return qs


class DomainQuerySet(QuerySet, DomainMixin):
    pass


class DomainManager(Manager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        return DomainQuerySet(self.model)


class DNSMixin(object):
    def by_change_perms(self, user, pk=None):
        if user.has_perm('dns.change_dnsrecord'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = get_objects_for_user(
                user,
                ['hosts.is_owner_host', 'hosts.change_host'],
                any_perm=True
            ).values_list('mac', flat=True)
            domain_perms = get_objects_for_user(
                user,
                ['dns.is_owner_domain', 'dns.change_domain'],
                any_perm=True
            ).values_list('name', flat=True)
            network_perms = get_objects_for_user(
                user,
                ['network.is_owner_network', 'network.change_network'],
                any_perm=True
            ).values_list('network', flat=True)

            qs = self.filter(
                Q(ip_content__host__in=host_perms) |
                Q(ip_content__network__in=network_perms)
            )

            domain_q_list = [Q(domain__name=domain) for domain in domain_perms]
            if domain_q_list:
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(mac=pk)
                return qs[0] if qs else None
            else:
                return qs


class DNSQuerySet(QuerySet, DNSMixin):
    pass


class DnsManager(Manager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        return DNSQuerySet(self.model)


    def add_or_update_record(self, user, name, content, dns_type, ttl=None, record=None):
        from openipam.dns.models import Domain

        try:
            if record:
                created = False
                dns_record = self.get(pk=record)
            else:
                created = True
                dns_record = self.model()


            # Permission Checks
            if created and not user.has_perm('dns.add_dnsrecord'):
                raise ValidationError('Invalid credentials: user %s does not have permissions'
                                      ' to add DNS records. Please contact an IPAM administrator.' % user)

            # Clear content if we are changing dnstype
            if created is False and dns_record.dns_type != dns_type:
                dns_record.clear_content()

            dns_record.dns_type = dns_type

            if dns_record.dns_type.is_a_record:
                address = Address.objects.get(address=content)
                dns_record.ip_content = address
            else:
                dns_record.text_content = content
                parsed_content = content.strip().split(' ')
                if dns_record.dns_type.is_mx_record and len(parsed_content) != 2:
                    raise ValidationError('Content for MX records need to have a priority and FQDN.')
                elif dns_record.dns_type.is_srv_record and len(parsed_content) != 4:
                    raise ValidationError('Content for SRV records need to only have a priority, weight, port, and FQDN.')
                else:
                    dns_record.set_priority()

            if ttl:
                dns_record.ttl = ttl

            dns_record.name = name
            dns_record.set_domain_from_name()

            allowed_domains = Domain.objects.by_dns_change_perms(user).filter(pk=dns_record.domain.pk)
            allowed_addresses = Address.objects.by_dns_change_perms(user)

            # Users must either have domain permissions, host permission or network permission.
            if not allowed_domains and not allowed_addresses.count():
                raise ValidationError('Invalid credentials: user %s does not have permissions'
                                  ' to add DNS records to the domain, host and/or network provided. Please contact an IPAM administrator '
                                  'to ensure you have the proper permissions.' % user)
            elif dns_record.dns_type.is_a_record and not allowed_addresses.filter(address=content):
                raise ValidationError('Invalid credentials: user %s does not have permissions'
                                  ' to add DNS records to the address provided. Please contact an IPAM administrator '
                                  'to ensure you have the proper host and/or network permissions.' % user)


            dns_record.changed_by = user

            dns_record.full_clean()

            dns_record.save()

            return dns_record, created

        except AddrFormatError:
            raise ValidationError('Invalid IP for content: %s' % content)

        except Address.DoesNotExist:
            raise ValidationError('Static IP does not exist for content: %s' % content)


class DnsTypeManager(Manager):

    @property
    def A(self):
        return self.get(name='A')

    @property
    def AAAA(self):
        return self.get(name='AAAA')

    @property
    def PTR(self):
        return self.get(name='PTR')

