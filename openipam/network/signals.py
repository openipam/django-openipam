from django.core.exceptions import ValidationError


def release_leases(sender, instance, **kwargs):
    from openipam.network.models import Lease

    if instance.host or not instance.pool:
        Lease.objects.filter(address=instance).delete()


def validate_address_type(sender, instance, action, **kwargs):
    if action == 'pre_add':
        if instance.pool:
            raise ValidationError('Address Types cannot have both a pool and a range.')


def delete_dns_record_for_static_host(sender, instance, *args, **kwargs):
    """
        Deletes A or AAAA and PTR records from address where hosts are removed.
    """
    if not instance.host:
        instance.release()
