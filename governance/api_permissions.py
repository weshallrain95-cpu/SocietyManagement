from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from governance.services.policy_guard import enforce_policy, PolicyDenied


class PolicyPermission(BasePermission):
    """
    DRF permission class backed by Governance Policy Engine.
    """

    # These must be defined on the View
    action: str | None = None
    resource: str | None = None

    def has_permission(self, request, view):
        if not self.action or not self.resource:
            raise AssertionError(
                "PolicyPermission requires 'action' and 'resource' to be set on the view."
            )

        actor_id = str(request.user.id) if request.user and request.user.is_authenticated else None

        attributes = {
            "role": getattr(request.user, "role", None),
            "is_authenticated": request.user.is_authenticated,
        }

        try:
            enforce_policy(
                actor_id=actor_id,
                action=self.action,
                resource=self.resource,
                attributes=attributes,
            )
            return True

        except PolicyDenied as e:
            raise PermissionDenied(str(e))
