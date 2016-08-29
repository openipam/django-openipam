from django.contrib.auth.models import update_last_login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import pagination

from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler

class UserAuthenticated(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = {
            "detail": "User is authenticated",
            "username": request.user.username,
            "is_superuser": request.user.is_superuser,
            "is_ipamadmin": request.user.is_ipamadmin,
        }
        return Response(data, status=status.HTTP_200_OK)


class APIPagination(pagination.LimitOffsetPagination):
    default_limit = 50
    limit_query_param = 'limit'
    max_limit = None

    def get_limit(self, request):
        ret = super(APIPagination, self).get_limit(request)
        if ret == 0:
            return self.max_limit
        return ret


class APIMaxPagination(pagination.LimitOffsetPagination):
    default_limit = 50
    limit_query_param = 'limit'
    max_limit = 5000

    def get_limit(self, request):
        ret = super(APIMaxPagination, self).get_limit(request)
        if ret == 0:
            return self.max_limit
        return ret


class TokenAuthenticationView(ObtainJSONWebToken):
    """Implementation of ObtainAuthToken with last_login update"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            update_last_login(None, user)
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_jwt_token = TokenAuthenticationView.as_view()