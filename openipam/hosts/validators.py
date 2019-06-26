from django.core.exceptions import ValidationError

import re


def validate_hostname(value):
    allowed = re.compile(r"(?i)^(([a-z0-9-]+\.)?[a-z0-9][a-z0-9-]*\.)+[a-z]{2,6}$")
    if not allowed.match(value):
        raise ValidationError(
            "Hostname not valid. Please use only numbers, letters, and dashes when creating hostnames."
        )


def validate_csv_file(value):
    if not value.name.endswith(".csv"):
        raise ValidationError("Please upload a valid CSV file.")
