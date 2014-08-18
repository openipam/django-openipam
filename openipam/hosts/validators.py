from django.core.exceptions import ValidationError

import re


def validate_hostname(value):
    allowed = re.compile('(?i)^(([a-z0-9-]+\.)?[a-z0-9][a-z0-9-]*\.)+[a-z]{2,6}$')
    if not allowed.match(value):
        raise ValidationError('Hostname not valid. Please use only numbers, letters, and dashes when creating hostnames.')
