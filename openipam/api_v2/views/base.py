"""Base API views."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet


# Using page number pagination for v2 API, rather than limit/offset pagination.
# We're using it for the following reasons:
# 1. It closely matches how the data will be displayed in the UI
# 2. It's easier to use in the UI, since we can just pass the page number
# 3. Matching how a database query might be made doesn't make sense for an API
class APIPagination(PageNumberPagination):
    """Pagination for API endpoints."""

    # I set these at 10 and 100 for a reason. This is what a paginated UI
    # is for.
    page_size = 10  # Current default page size
    page_size_query_param = "page_size"
    max_page_size = 100  # even 25 takes over a second to load for hosts

    # Scrolling is a lot less useful, as a long list of hosts, subnets, etc.
    # will blend together. This is why a paginated UI is better for this. This
    # isn't your social media feed.


class LogsPagination(APIPagination):
    """Pagination for logs endpoints."""

    # Logs are a lot less data, so we can increase the page size.
    # We also want to be able to see more logs at once.
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 500


class APIModelViewSet(ModelViewSet):
    """Base API viewset."""

    pagination_class = APIPagination
