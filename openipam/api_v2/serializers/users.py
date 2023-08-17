from openipam.user.models import User
from rest_framework import serializers
from django.contrib.auth.models import Group


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


class GroupField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        return data


class RestrictedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
        read_only_fields = (
            "id",
            "username",
        )


class UserSerializer(serializers.ModelSerializer):
    groups = GroupField(many=True, read_only=False, queryset=Group.objects.all())

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
            "is_superuser",
            "is_active",
            "last_login",
            "date_joined",
            "groups",
        )
        read_only_fields = (
            "id",
            "username",
            "last_login",
            "date_joined",
        )
