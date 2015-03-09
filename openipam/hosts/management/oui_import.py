from openipam.hosts.models import OUI
from django.db import transaction
import requests

import re

# manuf = 'https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf'
manuf = 'file:///usr/share/wireshark/manuf'

maxmask = 0xffffffffffff
maxbits = 48


def generate_mask(bits):
    if bits > 48:
        raise Exception("bits: %d" % bits)
    shift = maxbits - bits
    mask = (maxmask >> shift) << shift
    return mask


def mac_to_int(mac):
    mac = re.sub(':. -', '', mac)
    if len(mac) != 12:
        raise Exception("Bad MAC: %s" % mac)

    mac_int = int(mac, 16)

    return mac_int


def find_end(mac, bits):
    return hex(mac_to_int(mac) | generate_mask(bits))[2:]


@transaction.atomic
def import_ouis(manuf=manuf):
    OUI.all().delete()

    file_uri_prefix = 'file://'

    is_file = True if manuf[len(file_uri_prefix)] == file_uri_prefix else False

    if is_file:
        filename = manuf[len(file_uri_prefix):]
        lines = open(filename).readlines()
    else:
        data = requests.get(manuf)
        lines = data.text.split('\n')

    for line in lines:
        line = line.strip()
        if line and line[0] != '#':
            mask = None
            oui, rest = line.split('\t', 1)
            if '#' in rest and '[TR' not in rest:
                shortname, longname = rest.split('#', 1)
            else:
                shortname, longname = rest, rest

            if '/' in oui:
                oui, mask = oui.split('/')
                mask = int(mask)

            oui = re.sub('[.: \t\n-]', '', oui)

            if mask is None:
                if len(oui) == 6:
                    mask = maxbits / 2
                elif len(oui) == 12:
                    mask = maxbits
                else:
                    raise Exception("Failed to find mask for %s (%s, %s)" % (line, oui, mask))

            if len(oui) < 12:
                # pad with zeros on the right
                oui = [oui] + (12 - len(oui)) * ['0']
                oui = ''.join(oui)

            shortname = shortname.strip()
            longname = longname.strip()

            OUI.objects.create(start=oui, stop=find_end(oui, mask), shortname=shortname, name=longname)
