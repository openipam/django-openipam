from django.db.models import Model, Manager, Q

from openipam.hosts.models import Host

from guardian.shortcuts import get_objects_for_user


class DomainManager(Manager):

    def get_domains_owned_by_user(self, user, ids_only=False, names_only=False):
        domains = get_objects_for_user(user, 'dns.is_owner_domain')
        # domains = self.raw('''
        #     SELECT d.id FROM domains d
        #         INNER JOIN dns_domainuserobjectpermission dup ON dup.content_object_id = d.id AND dup.user_id = %s
        #         INNER JOIN auth_permission duap ON dup.permission_id = duap.id AND duap.codename = 'is_owner_domain'

        #     UNION

        #     SELECT d.id FROM domains d
        #         INNER JOIN dns_domaingroupobjectpermission dgp ON dgp.content_object_id = d.id
        #         INNER JOIN auth_permission dgap ON dgp.permission_id = dgap.id AND dgap.codename = 'is_owner_domain'
        #         INNER JOIN users_groups ug ON dgp.group_id = ug.group_id and ug.user_id = %s
        # ''', [user.pk, user.pk])

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        if ids_only:
            domain_names = [domain.pk for domain in domains]
            return tuple(domains)
        else:
            return domains


class DnsManager(Manager):
    pass
