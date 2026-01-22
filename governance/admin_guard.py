from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

from governance.services.policy_guard import enforce_policy, PolicyDenied


def enforce_admin_policy(
    *,
    request,
    action: str,
    resource: str,
    attributes: dict | None = None,
):
    """
    Enforce governance policy inside Django Admin.
    """

    user = request.user
    actor_id = str(user.id)

    attrs = {
        "role": getattr(user, "role", None),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }

    if attributes:
        attrs.update(attributes)

    try:
        enforce_policy(
            actor_id=actor_id,
            action=action,
            resource=resource,
            attributes=attrs,
        )
    except PolicyDenied as e:
        raise DjangoPermissionDenied(str(e))
