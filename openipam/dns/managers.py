from django.db.models import Model, Manager, Q


class DnsManager(Manager):

    def get_dns_records_for_host(self, host):

        from openipam.hosts.models import Host

        # If host is a mac address, call the object
        if not isinstance(host, Model):
            host = Host.objects.get(pk=host)

        #self.filter(Q(address__mac=mac) | )
