from rest_framework.permissions import BasePermission


class IsBrokerMember(BasePermission):
    message = "Switch to a broker role to do this."

    def has_permission(self, request, view):
        return bool(getattr(request.user, "active_membership", None))


class IsBrokerManager(IsBrokerMember):
    message = "Only the broker principal or a manager can do this."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.active_membership.can_manage


class IsBrokerAdmin(IsBrokerMember):
    message = "Only the agency Admin can do this."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.active_membership.is_admin


_LABELS = {"uploads": "Excel uploads", "blasts": "blasts", "add_staff": "adding field staff"}


def CanDo(perm: str):  # noqa: N802 - reads like a permission class at the call site
    """The Admin, or a manager the Admin has allowed to do `perm` (uploads | blasts | add_staff)."""

    class _CanDo(IsBrokerMember):
        message = f"Only the agency Admin can do this, or a manager the Admin has allowed ({_LABELS.get(perm, perm)})."

        def has_permission(self, request, view):
            return super().has_permission(request, view) and request.user.active_membership.can(perm)

    _CanDo.__name__ = f"CanDo_{perm}"
    return _CanDo


class IsVerifiedBroker(IsBrokerManager):
    message = "Your broker account is pending verification."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.active_membership.org.is_verified


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
