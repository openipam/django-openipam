from django.core.exceptions import ValidationError

import re


def validate_hostname(value):
    allowed = re.compile("(?=^.{1,254}$)(^(?:(?!\d+\.)[a-zA-Z0-9_\-]{1,63}\.?)+(?:[a-zA-Z]{2,})$)", re.IGNORECASE)
    if not allowed.match(value):
        raise ValidationError('Hostname not valid.')
