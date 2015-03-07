from openipam.hosts.models import OUI
from django.db import transaction
import requests

import re

manuf='https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf'

maxmask = 0xffffffffffff
maxbits = 48 

def generate_mask(bits):
    if bits > 48:
        raise Exception("bits: %d" % bits)
    shift = maxbits-bits
    mask = (maxmask >> shift) << shift
    return hex(mask)[2:]


@transaction.atomic
def import_ouis(manuf=manuf):
    OUI.all().delete()

    data = requests.get(manuf)
    lines = data.text.split('\n')
    #lines = open('/usr/share/wireshark/manuf').readlines()

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
                    mask = maxbits/2
                elif len(oui) == 12:
                    mask = maxbits
                else:
                    raise Exception("Failed to find mask for %s (%s, %s)" % (line, oui, mask))

            if len(oui) < 12:
                # pad with zeros on the right
                oui = [oui] + (12-len(oui))*['0']
                oui = ''.join(oui)

            shortname = shortname.strip()
            longname = longname.strip()

            #print '|'.join(map(repr,[oui, generate_mask(mask), mask, shortname, longname]))
            OUI.objects.create(oui=oui, mask=generate_mask(mask), shortname=shortname, name=longname)
