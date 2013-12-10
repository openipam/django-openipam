from django.db.models import Model, Manager, Q

from openipam.hosts.models import Host


class DomainManager(Manager):

    def get_domains_owned_by_user(self, user, ids_only=False, names_only=False):
        domains = self.raw('''
            SELECT d.id FROM domains d
                INNER JOIN dns_domainuserobjectpermission dup ON dup.content_object_id = d.id AND dup.user_id = %s
                INNER JOIN auth_permission duap ON dup.permission_id = duap.id AND duap.codename = 'is_owner_domain'

            UNION

            SELECT d.id FROM domains d
                INNER JOIN dns_domaingroupobjectpermission dgp ON dgp.content_object_id = d.id
                INNER JOIN auth_permission dgap ON dgp.permission_id = dgap.id AND dgap.codename = 'is_owner_domain'
                INNER JOIN users_groups ug ON dgp.group_id = ug.group_id and ug.user_id = %s
        ''', [user.pk, user.pk])

        if names_only:
            domain_names = [domain.name for domain in domains]
            return tuple(domain_names)

        domains = [domain.id for domain in domains]

        if ids_only:
            return tuple(domains)
        else:
            return self.filter(pk__in=domains)


class DnsManager(Manager):

    def get_dns_records_with_owner_perms(self, user, pk=None):

        user_groups = user.groups.all()

        qs = self.filter(
            (
                Q(ip_content__isnull=True) &
                (
                    Q(domain__user_permissions__user=user) |
                    Q(domain__group_permissions__group__in=user_groups)
                )
            ) |

            (
                Q(ip_content__host__user_permissions__user=user) |
                Q(ip_content__host__group_permissions__group__in=user_groups)
            )
        )

        return qs


    def filter_with_permissions(self, **kwargs):
        '''
        Returns a dictionary of { DNS record ID : permissions bitstring }
        for this user's overall permissions on the DNS records.

        @param records: a list of dictionaries of DNS records
        '''

        if not records:
            return [{}]

        try:
            names = [row['name'] for row in records]
        except Exception, e:
            raise error.NotImplemented("You likely did not supply a list of dictionaries of DNS records. Error was: %s" % e)

        records = self.filter(**kwargs)

        # Get the hosts who have names from above, then get the permissions for those hosts
        hosts = self.get_hosts( hostname=names )
        hosts = Host.objects.filter(hostname__in=[record.name for record in records])

        host_perms = self.find_permissions_for_hosts( hosts, alternate_perms_key=obj.hosts.c.hostname )
        host_perms = host_perms[0] if host_perms else {}

        # Get the domain permissions for these names
        fqdn_perms = self.find_domain_permissions_for_fqdns(names=names)
        fqdn_perms = fqdn_perms[0] if fqdn_perms else {}

        # Get the DNS types so that we can clear permissions to default if they can't read the type
        dns_types = self.get_dns_types( only_useable=True )
        dns_type_perms = {}
        # Have [ { 'id' : 0, 'name' : 'blah' }, ... ]
        for typename in dns_types:
            dns_type_perms[typename['id']] = typename
            # Now have { 0 : { ... dns dict ... }, 12 : { ... dns dict ... } ... }

        # Time to make the final permission set...
        permissions = {}

        # Initialize the permissions dictionary with my min_perms to GUARANTEE a result for every record input
        for rr in records:
            permissions[rr['id']] = str(self._min_perms)

        for rr in records:
            # For every record that was a host, add that permission set to the final result
            if host_perms.has_key(rr['name']):
                permissions[rr['id']] = str(Perms(permissions[rr['id']]) | host_perms[rr['name']])

            # For every record that was a domain, or had permissions via a domain, add in those permissions
            if fqdn_perms.has_key(rr['name']):
                permissions[rr['id']] = str(Perms(permissions[rr['id']]) | fqdn_perms[rr['name']])

            # If they cannot use the DNS type of this record, even if they have host
            # or domain perms over it, then they cannot modify it
            if not dns_type_perms.has_key(rr['tid']):
                permissions[rr['id']] = str(backend.db_default_min_permissions)

        return [permissions]

