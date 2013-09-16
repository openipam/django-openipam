from django import template
from django.utils.timezone import utc, localtime

register = template.Library()

@register.assignment_tag
def arp_filter(list, mac):
    filtered_list = filter(lambda x: x.mac == mac, list)
    if filtered_list:
        return localtime(filtered_list[0].stopstamp).strftime('%b %d, %Y %I:%M %p')
    else:
        return 'No Data'
