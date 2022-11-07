from django.db.models import Manager, Q
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text
from django.core.cache import cache

from functools import reduce

from guardian.shortcuts import get_objects_for_user, get_objects_for_group

import operator


class DomainQuerySet(QuerySet):
    def can_view(self, user, use_groups=False, ids_only=False, names_only=False):
        # Temporarily set superuser to false so we can get only permission relations
        User = get_user_model()
        perm_user = User.objects.get(pk=user.pk)

        domains = get_objects_for_user(
            perm_user, "dns.view_domain", use_groups=use_groups, with_superuser=False
        )

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        if ids_only:
            domain_names = [domain.pk for domain in domains]
            return tuple(domains)
        else:
            return domains

    def by_owner(self, user, use_groups=False, ids_only=False, names_only=False):
        # Temporarily set superuser to false so we can get only permission relations
        User = get_user_model()
        perm_user = User.objects.get(pk=user.pk)

        domains = get_objects_for_user(
            perm_user,
            "dns.is_owner_domain",
            use_groups=use_groups,
            with_superuser=False,
        )

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        if ids_only:
            domain_names = [domain.pk for domain in domains]
            return tuple(domains)
        else:
            return domains

    def by_change_perms(self, user_or_group, pk=None, ids_only=False, names_only=False):
        User = get_user_model()

        if isinstance(user_or_group, User) and (
            user_or_group.has_perm("dns.change_domain")
            or user_or_group.has_perm("dns.is_owner_domain")
        ):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            if isinstance(user_or_group, User):
                get_objects_for_user_or_group = get_objects_for_user
            elif isinstance(user_or_group, Group):
                get_objects_for_user_or_group = get_objects_for_group
            else:
                raise Exception("A valid user or goup must is required.")

            domain_perms = get_objects_for_user_or_group(
                user_or_group,
                ["dns.is_owner_domain", "dns.change_domain"],
                any_perm=True,
            ).values_list("name", flat=True)

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
        if user.has_perm("dns.change_domain") or user.has_perm("dns.is_owner_domain"):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            domain_perms = get_objects_for_user(
                user,
                [
                    "dns.is_owner_domain",
                    "dns.add_records_to_domain",
                    "dns.change_domain",
                ],
                any_perm=True,
            ).values_list("name", flat=True)

            qs = self.filter(name__in=list(domain_perms))

            if pk:
                qs = qs.filter(pk=pk).first()

            return qs


class DNSQuerySet(QuerySet):
    def by_change_perms(self, user_or_group, pk=None, ids_only=False):
        User = get_user_model()

        if isinstance(user_or_group, User) and user_or_group.has_perm(
            "dns.change_dnsrecord"
        ):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            if isinstance(user_or_group, User):
                get_objects_for_user_or_group = get_objects_for_user
            elif isinstance(user_or_group, Group):
                get_objects_for_user_or_group = get_objects_for_group
            else:
                raise Exception("A valid user or goup must is required.")

            host_perms = get_objects_for_user_or_group(
                user_or_group,
                ["hosts.is_owner_host", "hosts.change_host"],
                any_perm=True,
            )
            host_perms_mac_list = [host.mac for host in host_perms]
            host_perms_name_list = [host.hostname for host in host_perms]
            domain_perms = get_objects_for_user_or_group(
                user_or_group,
                ["dns.is_owner_domain", "dns.change_domain"],
                any_perm=True,
            ).values_list("name", flat=True)
            network_perms = get_objects_for_user_or_group(
                user_or_group,
                ["network.is_owner_network", "network.change_network"],
                any_perm=True,
            ).values_list("network", flat=True)

            qs = self.filter(
                Q(ip_content__host__in=host_perms_mac_list)
                | Q(text_content__in=host_perms_name_list)
                | Q(ip_content__network__in=network_perms)
            )

            domain_q_list = [Q(domain__name=domain) for domain in domain_perms]
            if domain_q_list:
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(mac=pk)
                return qs[0] if qs else None
            elif ids_only:
                return tuple([dnsrecord.pk for dnsrecord in qs])
            else:
                return qs


class DnsManager(Manager):
    def add_or_update_record(
        self, user, name, content, dns_type=None, host=None, ttl=None, record=None
    ):
        from openipam.network.models import Address
        from openipam.hosts.models import Host
        from openipam.dns.validators import validate_fqdn

        try:
            if name:
                validate_fqdn(name)

            if record:
                created = False
                if isinstance(record, self.model):
                    dns_record = record
                else:
                    dns_record = self.get(pk=record)
            else:
                created = True
                dns_record = self.model()

            dns_record.changed_by = user

            # Clear content if we are changing dnstype
            if created is False and dns_type and dns_type != dns_record.dns_type:
                dns_record.clear_content()

            # Change dns_type if not None
            if dns_type:
                dns_record.dns_type = dns_type

            if not content:
                raise ValidationError("Content is required to create a DNS record.")

            if dns_record.dns_type.is_a_record:
                address = Address.objects.select_related("host").get(address=content)
                dns_record.ip_content = address
                dns_record.host = dns_record.ip_content.host
            else:
                dns_record.text_content = content

            if dns_record.dns_type.name in ["PTR", "HINFO", "SSHFP"]:
                if host:
                    dns_record.host = host
                else:
                    host = Host.objects.filter(
                        addresses__arecords__name=content
                    ).first()
                    if not host:
                        raise ValidationError(
                            "An 'A' Record for '%s' needs to exists to create '%s' records."
                            % (content, dns_record.dns_type.name)
                        )
                    dns_record.host = host

            if ttl:
                dns_record.ttl = ttl

            dns_record.name = name
            dns_record.set_priority()
            dns_record.set_domain_from_name()

            dns_record.full_clean()

            dns_record.save()

            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=ContentType.objects.get_for_model(self.model).pk,
                object_id=dns_record.pk,
                object_repr=force_text(dns_record),
                action_flag=ADDITION if created else CHANGE,
            )

            return dns_record, created

        # This needs to go....too vague an exception
        # except ValidationError:
        #     raise ValidationError('Invalid IP for content: %s' % content)

        except Address.DoesNotExist:
            raise ValidationError("Static IP does not exist for content: %s" % content)


class DnsTypeManager(Manager):
    @property
    def _cached_queryset(self):
        queryset = cache.get("ipam_dns_types")
        if not queryset:
            queryset = list(super(DnsTypeManager, self).get_queryset().all())
            cache.set("ipam_dns_types", queryset)
        return queryset

    @property
    def A(self):
        filtered = [record for record in self._cached_queryset if record.name == "A"]
        return filtered[0] if filtered else None

    @property
    def AAAA(self):
        filtered = [record for record in self._cached_queryset if record.name == "AAAA"]
        return filtered[0] if filtered else None

    @property
    def PTR(self):
        filtered = [record for record in self._cached_queryset if record.name == "PTR"]
        return filtered[0] if filtered else None

    @property
    def MX(self):
        filtered = [record for record in self._cached_queryset if record.name == "MX"]
        return filtered[0] if filtered else None
