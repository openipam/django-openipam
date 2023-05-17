from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings

from openipam.user.utils.user_utils import populate_user_from_ldap

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class IPAMJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _("Invalid payload.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            try:
                return populate_user_from_ldap(username=username)
            except Exception:
                msg = _("User does not exist.")
                raise exceptions.AuthenticationFailed(msg)

            msg = _("Invalid signature.")
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.AuthenticationFailed(msg)

        return user
