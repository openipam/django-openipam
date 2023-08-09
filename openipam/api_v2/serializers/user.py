from rest_framework import serializers
from openipam.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_superuser",
            "is_staff",
            "is_active",
            "last_login",
            "date_joined",
            "groups",
        ]
