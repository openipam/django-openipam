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
    limit_query_param = "limit"
    max_limit = None

    def get_limit(self, request):
        ret = pagination._positive_int(
            request.query_params.get(self.limit_query_param, self.default_limit),
            strict=False,
            cutoff=self.max_limit,
        )
        if ret == 0:
            return self.max_limit
        return ret


class APIMaxPagination(pagination.LimitOffsetPagination):
    default_limit = 50
    limit_query_param = "limit"
    max_limit = 10000

    def get_limit(self, request):
        ret = pagination._positive_int(
            request.query_params.get(self.limit_query_param, self.default_limit),
            strict=False,
            cutoff=self.max_limit,
        )
        if ret == 0:
            return self.max_limit
        return ret


class TokenAuthenticationView(ObtainJSONWebToken):
    """Implementation of ObtainAuthToken with last_login update"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get("user") or request.user
            update_last_login(None, user)
            token = serializer.object.get("token")
            response_data = jwt_response_payload_handler(token, user, request)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_jwt_token = TokenAuthenticationView.as_view()
