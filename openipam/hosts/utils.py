from openipam.network.models import AddressType
from openipam.hosts.models import Host


def get_address_type(address):
    # This will check the assigned address of this host and
    # figure out the address type.  This is used so set the foreign key 'address_type'
    # as this is new functionality

    address_types = AddressType.objects.filter(ranges__isnull=False)
    for address_type in address_types:
        has_cidr = address_type.ranges.filter(range__net_contains_or_equals=address.address)
        if has_cidr:
            return address_type
        # for cidr in address_type.ranges.all():
        #     if address in cidr:
        #         return address_type

    return None


def set_address_type():
    hosts = Host.objects.filter(addresses__isnull=False)

    for host in hosts:
        address = host.addresses.all()

        if len(address) == 1:

            address = address[0]
            address_type = get_address_type(address)
        else:
            address_type = AddressType.objects.get_by_name('other')

        host.address_type = address_type
        host.save()
