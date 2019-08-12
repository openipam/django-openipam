from django import template
from django.utils.timezone import localtime

register = template.Library()


def arp_timestamp_filter(list, mac):
    filtered_list = [x for x in list if x.mac == mac]
    if filtered_list:
        return localtime(filtered_list[0].stopstamp).strftime("%Y-%m-%d %I:%M %p")
    else:
        return "No Data"


def arp_ip_filter(list, mac):
    filtered_list = [x for x in list if x.mac == mac]
    if filtered_list:
        return filtered_list[0].address
    else:
        return "No Data"


register.filter("arp_timestamp_filter", arp_timestamp_filter)
register.filter("arp_ip_filter", arp_ip_filter)
