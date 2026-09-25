from django.db import transaction
from django.utils import timezone

from apps.masterdata import resolver
from apps.status import services as status_svc
from common import crypto

from .models import KeyCustody, Listing

# What "Available now" can hold: on offer, or on hold (a token was paid but the deal can still fall through).
AVAILABLE_NOW_STATES = ("AVAILABLE", "AVAILABLE_UNCONFIRMED", "ON_HOLD")
OFF_LIST_STATES = ("LET", "SOLD", "OFF_MARKET")

LISTING_FIELDS = (
    "asking_rent",
    "asking_price",
    "deposit",
    "maintenance",
    "negotiable",
    "available_from",
    "brokerage_terms",
    "owner_name",
    "visibility",
    "private_notes",
)
# Fields that, when a broker states them, are also evidence about the unit itself.
UNIT_EVIDENCE = {"bhk": "bhk", "property_type": "property_type", "carpet_sqft": "carpet_area_sqft", "floor": "floor_no"}


class InventoryError(Exception):
    pass


@transaction.atomic
def create_listing(
    *,
    org,
    user,
    unit,
    txn_type: str,
    data: dict,
    attributes: dict | None = None,
    owner_phone: str | None = None,
    keys: dict | None = None,
    origin="manual",
    source_type="broker",
    report_available: bool = True,
    available_now: bool = True,
) -> tuple[Listing, bool]:
    """Create (or refresh) this org's claim on a unit. Returns (listing, created)."""
    from apps.owners.models import OwnerWithdrawal

    if OwnerWithdrawal.objects.filter(org=org, unit=unit, active=True).exists():
        # D14: the owner's decision on who represents the flat is final until they allow the firm again.
        raise InventoryError("The owner has removed your firm from this flat. You can ask the owner to add you back from the flat's page.")
    listing = Listing.objects.filter(org=org, unit=unit, txn_type=txn_type, archived_at__isnull=True).first()
    created = listing is None
    if created:
        listing = Listing(org=org, unit=unit, txn_type=txn_type, created_by=user, origin=origin, last_confirmed_at=timezone.now())
    for f in LISTING_FIELDS:
        if f in data and data[f] is not None:
            setattr(listing, f, data[f])
    if owner_phone:
        e164 = crypto.normalise_phone(owner_phone)
        listing.owner_phone_enc = crypto.encrypt(e164)
        listing.owner_phone_hash = crypto.phone_hash(e164)
    listing.last_confirmed_at = timezone.now()
    if available_now or created:
        listing.available_now = available_now
    listing.save()

    for field, attr_key in UNIT_EVIDENCE.items():
        if data.get(field) not in (None, ""):
            resolver.record(unit, attr_key, str(data[field]), source_type=source_type, user=user, org=org)
    for key, value in (attributes or {}).items():
        if value in (None, ""):
            continue
        resolver.record(unit, key, value, source_type=source_type, user=user, org=org)
    if listing.price:
        resolver.record(
            unit, "rent_expected" if txn_type == "RENT" else "price_expected", listing.price, source_type=source_type, user=user, org=org
        )
    if keys:
        set_keys(listing, **keys)
    if report_available:
        status_svc.report(
            unit, txn_type, "AVAILABLE", status_svc.Actor.broker(org, user), reason="listed", available_from=listing.available_from
        )
    return listing, created


def set_keys(listing: Listing, *, holder_type: str, holder_user=None, instructions: str = "") -> KeyCustody:
    KeyCustody.objects.filter(listing=listing, to_ts__isnull=True).update(to_ts=timezone.now())
    return KeyCustody.objects.create(
        org=listing.org, listing=listing, holder_type=holder_type, holder_user=holder_user, instructions_enc=crypto.encrypt(instructions)
    )


def current_keys(listing: Listing) -> KeyCustody | None:
    return listing.keys.filter(to_ts__isnull=True).order_by("-from_ts").first()


def flag_keys_for_handover(org_id, user_id) -> int:
    """ORG-03: keys held by a removed staff member are flagged at once."""
    return KeyCustody.objects.filter(org_id=org_id, holder_user_id=user_id, to_ts__isnull=True).update(needs_handover=True)


def repoint_unit(src_unit, dst_unit) -> None:
    """During a master-data merge: move every org's listing to the surviving unit (platform context)."""
    for listing in Listing.objects.filter(unit=src_unit, archived_at__isnull=True):
        clash = Listing.objects.filter(org_id=listing.org_id, unit=dst_unit, txn_type=listing.txn_type, archived_at__isnull=True).exists()
        if clash:
            listing.archived_at = timezone.now()
            listing.private_notes = (listing.private_notes + "\n[Archived: duplicate after master-data merge]").strip()
            listing.save(update_fields=["archived_at", "private_notes"])
        else:
            listing.unit = dst_unit
            listing.save(update_fields=["unit"])


@transaction.atomic
def report_status(
    listing: Listing, new_state: str, *, user, reason="", available_from=None, licence_end_date=None, on_behalf_of_owner=False
):
    actor_type = "owner_via_broker" if on_behalf_of_owner else "broker"
    st = status_svc.report(
        listing.unit,
        listing.txn_type,
        new_state,
        status_svc.Actor(actor_type, org=listing.org, user=user),
        reason=reason,
        available_from=available_from,
        licence_end_date=licence_end_date,
    )
    listing.last_confirmed_at = timezone.now()
    if st.state in OFF_LIST_STATES:
        listing.available_now = False
    listing.save(update_fields=["last_confirmed_at", "available_now"])
    return st


def set_available_now(listings, on: bool, *, user) -> int:
    """The broker builds their "Available now" list from all their flats. Turning a flat on that is marked
    rented out, sold or off the market reports it as available again (unconfirmed until the owner says so)."""
    from apps.audit.services import audit

    changed = 0
    for listing in listings:
        if on and status_svc.get_status(listing.unit, listing.txn_type).state not in AVAILABLE_NOW_STATES:
            report_status(listing, "AVAILABLE", user=user, reason="made available now")
        if listing.available_now != on:
            listing.available_now = on
            listing.save(update_fields=["available_now", "updated_at"])
            audit(user, "listing.available_now" if on else "listing.not_available_now", listing, {})
            changed += 1
    return changed
