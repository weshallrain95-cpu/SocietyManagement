from society.models import (
    FlatOwnership,
    FlatOwner,
)


def resolve_person_for_flat(
    flat,
):

    ownership = (
        FlatOwnership.objects.filter(
            flat=flat,
            is_active=True,
        )
        .order_by("-id")
        .first()
    )

    if not ownership:
        return None

    owner = (
        FlatOwner.objects.filter(
            ownership=ownership,
        )
        .select_related("person")
        .first()
    )

    if not owner:
        return None

    if not owner.person:
        return None

    return owner.person