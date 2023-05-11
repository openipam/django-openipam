from openipam.hosts.models import (
    FreeformAttributeToHost,
    StructuredAttributeValue,
    Host,
)
from openipam.network.models import AddressType, Network
from openipam.user.models import User
from django.contrib.auth.models import Group
from django.db.models import Q
from django.views import View
from functools import reduce
from django.http import JsonResponse

from .serializers import AutocompleteSerializer

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


# class IPAMSearchAutoComplete(generics.ListAPIView):
#     models_to_search = []

#     model_fields = {
#         User: ["username", "first_name", "last_name"],
#         Group: ["name"],
#         Network: ["network", "name"],
#         StructuredAttributeValue: ["attribute__name", "value"],
#         FreeformAttributeToHost: ["attribute__name", "value"],
#         AddressType: ["name", "description"],
#     }

#     serializer_class = AutocompleteSerializer

#     def get_queryset(self):
#         return self.models_to_search[0].objects.all()

#     def get_filter_fields(self):


#     @classmethod
#     def for_hosts(self):
#         """Advanced search for hosts"""

#         return self.using_models(
#             User,
#             Group,
#             Network,
#             StructuredAttributeValue,
#             FreeformAttributeToHost,
#             AddressType,
#         )

#     @classmethod
#     def using_models(cls, *models):
#         """Search the specified models."""

#         # Create a new class that inherits from this class and set the
#         # models_to_search attribute to the specified models.
#         new_class = type(cls.__name__, (cls,), {})
#         new_class.models_to_search = models
#         return new_class


class IPAMSearchAutoComplete(View):
    @classmethod
    def searching_models(cls, *models):
        """Search the specified models."""

        # Create a new class that inherits from this class and set the
        # models_to_search attribute to the specified models.
        new_class = type(cls.__name__, (cls,), {})
        new_class._models_to_search = models
        return new_class

    @classmethod
    def for_hosts(cls):
        """Advanced search for hosts"""
        return cls.searching_models(
            User,
            Group,
            Network,
            StructuredAttributeValue,
            FreeformAttributeToHost,
            AddressType,
        )

    _models_to_search = []

    # All of the models that this class supports searching. If it is not
    # in here, it will not be searched.
    _search_fields = {
        User: ["username", "first_name", "last_name"],
        Group: ["name"],
        Network: ["network", "name"],
        StructuredAttributeValue: ["attribute__name", "value"],
        FreeformAttributeToHost: ["attribute__name", "value"],
        AddressType: ["name", "description"],
    }

    _formatters = {
        FreeformAttributeToHost: lambda x: ["Attribute", x.attribute, x.value],
        StructuredAttributeValue: lambda x: ["Attribute", x.attribute, x.value],
        Network: lambda x: ["Network", x.name, x],
        AddressType: lambda x: ["Address Type", x],
        User: lambda x: ["User", x, x.get_full_name()],
        Group: lambda x: ["Group", x],
    }

    def get_queryset(self, model_class=None):
        if not model_class:
            querysets = [self.get_queryset(model) for model in self._models_to_search]
            return querysets
        else:
            try:
                return model_class.objects.all().filter(
                    self.get_search_filters(model_class)
                )[
                    :5
                ]  # Limit to 3 results per model
            except KeyError:
                # If the model is not in _search_fields, return an empty queryset.
                return model_class.objects.none()

    def get_search_filters(self, model_class):
        # Produce a list of filters for each field in _search_fields for this model.
        filters = [
            Q(**{f"{field}__icontains": self.q})
            # Let this throw a KeyError if the model is not in _search_fields.
            # We'll catch it in get_queryset and return an empty queryset.
            for field in self._search_fields[model_class]
        ]

        # Reduce into a single filter that ORs all of the filters together.
        return reduce(lambda x, y: x | y, filters)

    def serialize(self, obj):
        model_class = obj.__class__

        try:
            formatted = self._formatters[model_class](obj)
            formatted = [str(x) for x in formatted]
            return " | ".join(formatted)
        except KeyError:
            # If the model is not in _formatters, use a fallback that relies on
            # the model's __str__ method.
            return f"{model_class.__name__} | {obj}"

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get("q", "")
        if len(self.q) < 2:
            return {"results": []}
        querysets = self.get_queryset()
        # results = [*queryset for queryset in querysets]
        results = []
        for queryset in querysets:
            results.extend(queryset)

        return JsonResponse(
            {
                "results": [
                    {"id": obj.pk, "text": self.serialize(obj)} for obj in results
                ]
            }
        )


class IPAMSearchAutoCompleteUsingDAL(autocomplete.Select2QuerySetSequenceView):
    split_words = True

    attrs = {"minimum_characters": 2, "placeholder": "Advanced Search"}

    def get_queryset(self):
        queryset = self.mixup_querysets(
            autocomplete.QuerySetSequence(
                self.get_filtered_queryset(User),
                self.get_filtered_queryset(Group),
                self.get_filtered_queryset(Network),
                self.get_filtered_queryset(StructuredAttributeValue),
                self.get_filtered_queryset(FreeformAttributeToHost),
                self.get_filtered_queryset(AddressType),
                self.get_filtered_queryset(Host),
            )
        )

        return queryset

    def get_filtered_queryset(self, model_class):
        return model_class.objects.all().filter(self.get_search_filters(model_class))

    search_fields = {
        Network: ["network", "name"],
        Host: ["hostname", "mac"],
        User: ["username", "first_name", "last_name"],
        Group: ["name"],
        StructuredAttributeValue: ["attribute__name", "value"],
        FreeformAttributeToHost: ["attribute__name", "value"],
        AddressType: ["name", "description"],
    }
    # search_fields = [
    #     ("network", "name"),
    #     ("username", "^first_name", "^last_name"),
    #     ("^name",),
    #     ("attribute__name", "value"),
    #     ("attribute__name", "value"),
    #     ("name", "description"),
    # ]

    def get_search_filters(self, model_class):
        filters = [
            Q(**{f"{field}__icontains": self.q})
            for field in self.search_fields[model_class]
        ]
        return reduce(lambda x, y: x | y, filters)

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
