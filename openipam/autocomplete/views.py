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
