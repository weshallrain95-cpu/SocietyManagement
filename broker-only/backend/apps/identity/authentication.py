from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from common import rls


class OrgAwareJWTAuthentication(JWTAuthentication):
    """JWT auth that also establishes the broker-org RLS context for the request.

    The token carries ``org`` (active broker org) and ``role``. The membership is
    re-checked on every request so removing a staff member takes effect at once.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        user.active_org_id = None
        user.active_role = token.get("role", "customer")
        user.active_membership = None
        org_id = token.get("org")
        if org_id:
            from apps.orgs.models import Membership

            m = Membership.objects.filter(user=user, org_id=org_id, active=True).select_related("org").first()
            if not m:
                raise AuthenticationFailed("Your access to this broker organisation has ended.")
            user.active_org_id = m.org_id
            user.active_role = m.role
            user.active_membership = m
            rls.set_org(m.org_id)
        return user, token
