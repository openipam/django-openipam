from openipam.user.models import User
from rest_framework import serializers


class UserNestedSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs["read_only"] = True
        super(UserNestedSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_ipamadmin",
        )
        read_only_fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_ipamadmin",
        )
