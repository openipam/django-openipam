from openipam.hosts.models import (
    FreeformAttributeToHost,
    StructuredAttributeValue,
)
from openipam.network.models import AddressType, Network
from openipam.user.models import User
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.views import View
from functools import reduce
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType


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
            AddressType,
        )

    @classmethod
    def enable_word_split(cls):
        new_class = type(cls.__name__, (cls,), {})
        new_class._word_split = True
        return new_class

    @classmethod
    def always_use_pk(cls):
        new_class = type(cls.__name__, (cls,), {})
        new_class._default_id_generator = lambda self, x: x.pk
        new_class._id_generators = {}
        return new_class

    _word_split = False

    def _default_id_generator(self, x):
        f"{x.__class__.__name__.lower()}:{x.pk}"

    _id_generators = {
        User: lambda x: f"user:{x.username}",
        Group: lambda x: f"group:{x.name}",
        Network: lambda x: f"net:{x.network}",
        StructuredAttributeValue: lambda x: f"sattr:{x.value}",
        AddressType: lambda x: f"atype:{x.pk}",
    }

    _models_to_search = []

    # All of the models that this class supports searching. If it is not
    # in here, it will not be searched.
    _search_fields = {
        User: ["username", "first_name", "last_name", "email"],
        Group: ["name"],
        Network: ["network", "name"],
        StructuredAttributeValue: ["attribute__name", "value"],
        AddressType: ["name", "description"],
        Permission: ["name", "codename", "content_type__app_label"],
        ContentType: ["app_label", "model"],
    }

    _formatters = {
        StructuredAttributeValue: lambda x: ["Attribute", x.attribute, x.value],
        Network: lambda x: ["Network", x.name, x],
        AddressType: lambda x: ["Address Type", x],
        User: lambda x: ["User", x, x.get_full_name()],
        Group: lambda x: ["Group", x],
        Permission: lambda x: ["Permission", x.content_type.app_label, x.name],
        ContentType: lambda x: ["Content Type", x.app_label, x.model],
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
        filters = []
        for q in self.q:
            filters.append(
                [
                    Q(**{f"{field}__icontains": q})
                    for field in self._search_fields[model_class]
                ]
            )

        # OR all of the filters for each query together.
        filters = [reduce(lambda x, y: x | y, filter) for filter in filters]

        # AND all of the filters for each field together.
        return reduce(lambda x, y: x & y, filters)

    def serialize(self, obj):
        model_class = obj.__class__

        try:
            formatted = self._formatters[model_class](obj)
            formatted = [str(x) for x in formatted]
            if len(self._models_to_search) == 1:
                # If there is only one model, don't show the model name. The
                # user should already know what they're searching for.
                formatted = formatted[1:]
            return " | ".join(formatted)
        except KeyError:
            # If the model is not in _formatters, use a fallback that relies on
            # the model's __str__ method.
            if len(self._models_to_search) == 1:
                return str(obj)
            else:
                return f"{model_class.__name__} | {obj}"

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get("q", "")
        if len(self.q) < 2:
            return JsonResponse({"results": []})
        if self._word_split:
            # treat each word as a separate query
            self.q = self.q.split(" ")
        else:
            self.q = [self.q]
        querysets = self.get_queryset()
        # results = [*queryset for queryset in querysets]
        results = []
        for queryset in querysets:
            results.extend(queryset)

        # Generate the ID used to identify the object in the results.
        def get_id(obj):
            try:
                return self._id_generators[obj.__class__](obj)
            except KeyError:
                # If the model is not in _id_generators, use a fallback that
                # relies on the model's pk.
                return self._default_id_generator(obj)

        results = [
            {
                "id": get_id(obj),
                "text": self.serialize(obj),
            }
            for obj in results
        ]

        return JsonResponse(
            {
                "results": results,
            }
        )


GroupAutocomplete = IPAMSearchAutoComplete.searching_models(Group).always_use_pk()
UserAutocomplete = (
    IPAMSearchAutoComplete.searching_models(User).enable_word_split().always_use_pk()
)
PermissionsAutocomplete = (
    IPAMSearchAutoComplete.searching_models(Permission)
    .enable_word_split()
    .always_use_pk()
)
ContentTypeAutocomplete = (
    IPAMSearchAutoComplete.searching_models(ContentType)
    .enable_word_split()
    .always_use_pk()
)
