from rest_framework import serializers as lib_serializers
from openipam.hosts.models import StructuredAttributeValue, Attribute


class StructuredAttributeValueSerializer(lib_serializers.ModelSerializer):
    changed_by = lib_serializers.ReadOnlyField(source="changed_by.username")

    # This serializer should return None if the related attribute is not structured
    def to_representation(self, instance):
        if instance.attribute.structured:
            return super().to_representation(instance)
        else:
            return None

    class Meta:
        model = StructuredAttributeValue
        fields = "__all__"


class AttributeSerializer(lib_serializers.ModelSerializer):
    changed_by = lib_serializers.ReadOnlyField(source="changed_by.username")
    choices = lib_serializers.SerializerMethodField()
    # Uncomment this if the categories I added are ever merged
    # category = lib_serializers.ReadOnlyField(source="category.name")

    def get_choices(self, obj):
        if obj.structured:
            return StructuredAttributeValueSerializer(obj.choices.all(), many=True).data
        else:
            return None

    class Meta:
        model = Attribute
        fields = "__all__"
