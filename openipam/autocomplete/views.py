from openipam.hosts.models import FreeformAttributeToHost, StructuredAttributeValue
from openipam.network.models import AddressType, Network
from openipam.user.models import User
from django.contrib.auth.models import Group

from dal import autocomplete


class UserAutocomplete(autocomplete.Select2QuerySetView):
    search_fields = ["^username", "^first_name", "^last_name", "email"]
    attrs = {"placeholder": "Search Users"}
    split_words = True
    model = User

    def get_result_label(self, result):
        if result.get_full_name():
            return f"{result.username} | {result.get_full_name()}"
        return str(result)


class GroupAutocomplete(autocomplete.Select2QuerySetView):
    search_fields = ["name"]
    attrs = {"placeholder": "Search Groups"}
    model = Group


class IPAMSearchAutoComplete(autocomplete.Select2QuerySetSequenceView):
    split_words = True

    attrs = {"minimum_characters": 2, "placeholder": "Advanced Search"}

    def get_queryset(self):
        return self.mixup_querysets(
            autocomplete.QuerySetSequence(
                Network.objects.all(),
                User.objects.all(),
                Group.objects.all(),
                StructuredAttributeValue.objects.all(),
                FreeformAttributeToHost.objects.all(),
                AddressType.objects.all(),
            )
        )

    search_fields = [
        ("network", "name"),
        ("username", "^first_name", "^last_name"),
        ("^name",),
        ("attribute__name", "value"),
        ("attribute__name", "value"),
        ("name", "description"),
    ]

    def choice_label(self, choice):
        if choice.__class__.__name__ == "User":
            return "%s | %s | %s" % (
                choice.__class__.__name__,
                choice,
                choice.get_full_name(),
            )
        elif choice.__class__.__name__ in [
            "StructuredAttributeValue",
            "FreeformAttributeToHost",
        ]:
            return "%s | %s | %s" % ("Attribute", choice.attribute, choice.value)
        elif choice.__class__.__name__ == "AddressType":
            return "%s | %s" % ("Address Type", choice)
        elif choice.__class__.__name__ == "Network":
            return "%s | %s | %s" % ("Network", choice.name, choice)
        else:
            return "%s | %s" % (choice.__class__.__name__, choice)

    def choice_value(self, choice):
        if choice.__class__.__name__ == "User":
            return "user:%s" % choice.username
        elif choice.__class__.__name__ == "Group":
            return "group:%s" % choice.name
        elif choice.__class__.__name__ == "Network":
            return "net:%s" % choice.network
        elif choice.__class__.__name__ == "StructuredAttributeValue":
            return "sattr:%s" % choice.value
        elif choice.__class__.__name__ == "FreeformAttributeToHost":
            return "fattr:%s" % choice.value
        elif choice.__class__.__name__ == "AddressType":
            return "atype:%s" % choice.pk
