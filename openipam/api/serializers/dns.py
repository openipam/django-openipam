from rest_framework import serializers

from openipam.dns.models import Domain


class DomainNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('name',)


class DomainSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username

    class Meta:
        model = Domain
