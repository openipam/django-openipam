

def create_dns_record_for_static_host(sender, instance, created, *args, **kwargs):
    """
        Creates A or AAAA and PTR records for newely created hosts.
    """
    if not instance.is_dynamic:
        addresses = instance.addresses.all()

        #assert False, addresses
        if addresses:
            for address in addresses:

                from openipam.dns.models import DnsRecord, DnsType

                # We only create if these record do not exist.  Is this good?
                existing_ptr = DnsRecord.objects.filter(name=address.address.reverse_dns[:-1])
                existing_a = DnsRecord.objects.filter(ip_content=address.address.format())

                if not existing_ptr:
                    new_ptr = DnsRecord()
                    new_ptr.dns_type = DnsType.objects.get(name='PTR')
                    new_ptr.name = address.address.reverse_dns[:-1]
                    new_ptr.set_domain_from_name()
                    new_ptr.text_content = instance.hostname
                    new_ptr.changed_by = instance.changed_by
                    new_ptr.save()

                if not existing_a:
                    if address.address.version == 4:
                        dns_type =  DnsType.objects.get(name='A')
                    elif address.address.version == 6:
                        dns_type =  DnsType.objects.get(name='AAAA')
                    else:
                        raise Exception('No A record Type for IP Address')

                    new_a = DnsRecord()
                    new_a.dns_type = dns_type
                    new_a.name = instance.hostname
                    new_a.set_domain_from_name()
                    new_a.ip_content = address
                    new_a.changed_by = instance.changed_by
                    new_a.save()


def delete_dns_record_for_static_host(sender, instance, *args, **kwargs):
    """
        Deletes A or AAAA and PTR records hosts that are deleted.
    """
    if not instance.is_dynamic:
        addresses = instance.addresses.all()

        if addresses:
            for address in addresses:

                from openipam.dns.models import DnsRecord

                # Delete PTR records
                DnsRecord.objects.filter(name=address.address.reverse_dns[:-1]).delete()
                # Delete A or AAAA records
                DnsRecord.objects.filter(ip_content=address.address.format()).delete()


