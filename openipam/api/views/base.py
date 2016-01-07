from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import pagination


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
