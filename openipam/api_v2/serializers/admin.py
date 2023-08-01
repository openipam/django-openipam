from django.contrib.admin.models import LogEntry
from rest_framework import serializers
from openipam.log.models import EmailLog


class LogEntrySerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(read_only=True, slug_field="model")

    class Meta:
        model = LogEntry
        fields = "__all__"


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = "__all__"
