from django.db.models import Model, Manager, Q
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from openipam.hosts.models import Host
from openipam.network.models import Address

from guardian.shortcuts import get_objects_for_user

from netaddr.core import AddrFormatError


class DomainMixin(object):
    def by_owner(self, user, use_groups=False, ids_only=False, names_only=False):
        domains = get_objects_for_user(user, 'dns.is_owner_domain', use_groups=use_groups)

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        if ids_only:
            domain_names = [domain.pk for domain in domains]
            return tuple(domains)
        else:
            return domains


class DomainQuerySet(QuerySet, DomainMixin):
    pass


class DomainManager(Manager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        return DomainQuerySet(self.model)


class DnsManager(Manager):

    def add_or_update_record(self, user, name, content, dns_type, ttl=None, record=None):
        try:
            if record:
                created = False
                dns_record = self.get(pk=record)
            else:
                created = True
                dns_record = self.model()

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
            dns_record.changed_by = user

            dns_record.full_clean()

            if not dns_record.user_has_ownership(user):
                raise ValidationError('Invalid credentials: user %s does not have permissions'
                                      ' to add/modify this record.' % user)
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

