from rest_framework import serializers as lib_serializers
from openipam.hosts.models import StructuredAttributeValue, Attribute


class AttributeSerializer(lib_serializers.ModelSerializer):
    changed_by = lib_serializers.ReadOnlyField(source="changed_by.username")
    structured_values = lib_serializers.SerializerMethodField()

    def get_structured_values(self, obj):
        if not obj.structured:
            return None
        return obj.choices.values_list("value", flat=True)

    class Meta:
        model = Attribute
        fields = "__all__"
