from rest_framework.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"


class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"

    def allow_request(self, request, view):
        if request.user.is_ipamadmin:
            # If the user is an administrator, they may legitimately need to make
            # more than 1000 requests per day. Allow them to do so.
            return True
        return super().allow_request(request, view)
