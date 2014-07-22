from django import template
from django.utils.timezone import localtime

register = template.Library()

@register.assignment_tag
def arp_timestamp_filter(list, mac):
    filtered_list = filter(lambda x: x.mac == mac, list)
    if filtered_list:
        return localtime(filtered_list[0].stopstamp).strftime('%Y-%m-%d %I:%M %p')
    else:
        return 'No Data'

@register.assignment_tag
def arp_ip_filter(list, mac):
    filtered_list = filter(lambda x: x.mac == mac, list)
    if filtered_list:
        return filtered_list[0].address
    else:
        return 'No Data'
