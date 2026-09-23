"""Side effects of status changes, run by the outbox relay (platform context)."""
from common.events import handles
from common.notify import notify_org


@handles("unit_status.changed")
def tell_other_brokers(payload: dict) -> None:
    """Other brokers holding a listing on the unit learn the new state, never who changed it."""
    from apps.inventory.models import Listing

    orgs = (
        Listing.objects.filter(unit_id=payload["unit_id"], txn_type=payload["txn_type"], archived_at__isnull=True)
        .exclude(org_id=payload.get("actor_org_id"))
        .values_list("org_id", "id")
    )
    for org_id, listing_id in orgs:
        notify_org(
            org_id,
            "unit_status_changed",
            {"listing_id": str(listing_id), "to_state": payload["to_state"], "note": "Reported by another source"},
            realtime_event="status.changed",
        )
