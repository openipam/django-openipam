from rest_framework import serializers

from openipam.dns.models import Domain


class DomainNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        fields = ('name',)
