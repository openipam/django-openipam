"""Base API views."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet


# Using page number pagination for v2 API, rather than limit/offset pagination.
class APIPagination(PageNumberPagination):
    """Pagination for API endpoints."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 1000


class APIModelViewSet(ModelViewSet):
    """Base API viewset."""

    pagination_class = APIPagination
