from rest_framework.permissions import BasePermission


class IsBrokerMember(BasePermission):
    message = "Switch to a broker role to do this."

    def has_permission(self, request, view):
        return bool(getattr(request.user, "active_membership", None))


class IsBrokerManager(IsBrokerMember):
    message = "Only the broker principal or a manager can do this."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.active_membership.can_manage


class IsVerifiedBroker(IsBrokerManager):
    message = "Your broker account is pending verification."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.active_membership.org.is_verified


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
