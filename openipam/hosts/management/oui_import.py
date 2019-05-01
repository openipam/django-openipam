from openipam.hosts.models import OUI
from django.db import transaction
import requests

import re

# manuf = 'https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf'
manuf = "file:///usr/share/wireshark/manuf"

maxmask = 0xFFFFFFFFFFFF
maxbits = 48


def generate_mask(bits):
    if bits > 48:
        raise Exception("bits: %d" % bits)
    shift = maxbits - bits
    mask = (maxmask >> shift) << shift
    return mask


def mac_to_int(mac):
    mac = re.sub(":. -", "", mac)
    if len(mac) != 12:
        raise Exception("Bad MAC: %s" % mac)

    mac_int = int(mac, 16)

    return mac_int


def int_to_mac(mac):
    s = hex(mac)[2:]
    s = "".join(["0"] * (12 - len(s)) + [s])
    return s


def find_end(mac, bits):
    return int_to_mac((mac_to_int(mac) | (~generate_mask(bits)) & maxmask))


@transaction.atomic
def import_ouis(manuf=manuf):
    OUI.objects.all().delete()

    file_uri_prefix = "file://"

    is_file = True if manuf[len(file_uri_prefix)] == file_uri_prefix else False

    if is_file:
        filename = manuf[len(file_uri_prefix) :]
        lines = open(filename).readlines()
    else:
        data = requests.get(manuf)
        lines = data.text.split("\n")

    for line in lines:
        line = line.strip()
        if line and line[0] != "#":
            maskbits = None
            oui, rest = line.split("\t", 1)
            if "#" in rest and "[TR" not in rest:
                shortname, longname = rest.split("#", 1)
            else:
                shortname, longname = rest, rest

            if "/" in oui:
                oui, maskbits = oui.split("/")
                maskbits = int(maskbits)

            oui = re.sub("[.: \t\n-]", "", oui)

            if maskbits is None:
                if len(oui) == 6:
                    maskbits = maxbits / 2
                elif len(oui) == 12:
                    maskbits = maxbits
                else:
                    raise Exception(
                        "Failed to find mask for %s (%s, %s)" % (line, oui, maskbits)
                    )

            if len(oui) < 12:
                # pad with zeros on the right
                oui = [oui] + (12 - len(oui)) * ["0"]
                oui = "".join(oui)

            shortname = shortname.strip()
            longname = longname.strip()

            OUI.objects.create(
                start=oui,
                stop=find_end(oui, maskbits),
                shortname=shortname,
                name=longname,
            )
