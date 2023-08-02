from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from rest_framework import serializers
from openipam.log.models import EmailLog


class LogEntrySerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(read_only=True, slug_field="model")
    action_flag = serializers.SerializerMethodField()

    def get_action_flag(self, obj: LogEntry):
        if obj.action_flag == ADDITION:
            return "Addition"
        elif obj.action_flag == CHANGE:
            return "Change"
        elif obj.action_flag == DELETION:
            return "Deletion"
        else:
            # this shouldn't happen, but just in case
            return obj.action_flag

    class Meta:
        model = LogEntry
        fields = "__all__"


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = "__all__"
