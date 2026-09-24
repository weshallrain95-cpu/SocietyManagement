"""Owner journeys (OWN-01..06) and the broker side of owner decisions (INV-08, D13, D14)."""

from datetime import date

from django.conf import settings
from django.contrib.gis.measure import D
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.services import audit
from apps.inventory.models import Listing
from apps.masterdata import resolver
from apps.masterdata.layout import check_flat
from apps.masterdata.models import OwnershipClaim, Society, Unit
from apps.masterdata.services import get_or_create_building, get_or_create_unit
from apps.orgs.models import BrokerOrg, Membership
from apps.status.models import UnitStatus
from common import rls
from common.notify import notify_org, notify_user, queue_for_admin

from . import media as m
from .models import OwnerInvite, OwnerWithdrawal, UnitMedia

ACTIVE_CLAIM = [OwnershipClaim.Status.DECLARED, OwnershipClaim.Status.VERIFIED, OwnershipClaim.Status.PENDING]
TERMS_FIELDS = {"txn_type", "expected_rent", "expected_price", "deposit", "available_from", "note"}
HOUSE_RULES = {"pets_allowed", "nonveg_cooking", "bachelors_allowed", "smoking_allowed"}
NEARBY_M = 5000


class OwnerError(Exception):
    pass


def my_claims(user):
    return (
        OwnershipClaim.objects.filter(user=user, status__in=ACTIVE_CLAIM)
        .select_related("unit__building__society__locality")
        .order_by("-created_at")
    )


# --- registering a flat -------------------------------------------------------------------------


@transaction.atomic
def register_flat(user, *, society: Society, wing: str | None, unit_no: str, bhk, proof, declared: bool, floor=None) -> OwnershipClaim:
    """Route 1: the owner puts their own flat on the platform. Proof is kept, never checked (D14)."""
    if not declared:
        raise OwnerError("Please confirm that you own this flat")
    if proof is None:
        raise OwnerError("Add a photo or PDF of your ownership proof (index II, share certificate or electricity bill)")
    society = society.resolved()
    chk = check_flat(society, wing, unit_no, floor)
    if chk["blocking"]:
        raise OwnerError(next(i.message for i in chk["issues"] if i.blocking))
    building = get_or_create_building(society, chk["wing"])
    unit, _ = get_or_create_unit(building, unit_no, bhk=bhk, floor=floor)
    mine = OwnershipClaim.objects.filter(unit=unit, user=user, status__in=ACTIVE_CLAIM).first()
    if mine:
        return mine
    try:
        doc = m.process_document(proof)
    except m.MediaError as e:
        raise OwnerError(str(e)) from e
    claim = OwnershipClaim.objects.create(unit=unit, user=user, proof_type="document", status=OwnershipClaim.Status.DECLARED)
    UnitMedia.objects.create(unit=unit, claim=claim, kind=UnitMedia.Kind.DOCUMENT, uploaded_by=user, **doc)
    others = OwnershipClaim.objects.filter(unit=unit, status__in=ACTIVE_CLAIM).exclude(user=user).count()
    if others:  # not a block: the proof on file is what matters if it is ever disputed
        queue_for_admin("ownership_conflict", unit, f"{others + 1} people say they own {unit}", {"claim_id": str(claim.pk)})
    audit(user, "owner.flat_registered", unit, {"claim": str(claim.pk)})
    return claim


def set_terms(claim: OwnershipClaim, *, terms: dict, house_rules: dict, user) -> OwnershipClaim:
    claim.terms = {k: v for k, v in terms.items() if k in TERMS_FIELDS and v not in (None, "")}
    claim.save(update_fields=["terms"])
    for key, value in house_rules.items():
        if key in HOUSE_RULES and value not in (None, ""):
            resolver.record(claim.unit, key, value, source_type="owner_verified", user=user)  # owner answers win (Data Model §6)
    return claim


# --- photos and videos ------------------------------------------------------------------------------


def add_media(claim: OwnershipClaim, upload, *, user, caption: str = "") -> UnitMedia:
    kind = m.kind_for(upload)
    live = UnitMedia.objects.filter(unit=claim.unit, kind=kind, deleted_at__isnull=True).count()
    cap = settings.OB_MAX_VIDEOS_PER_FLAT if kind == "video" else settings.OB_MAX_PHOTOS_PER_FLAT
    if live >= cap:
        raise OwnerError(f"A flat can have up to {cap} {kind}s — delete one first")
    try:
        data = m.process_video(upload) if kind == "video" else m.process_photo(upload)
    except m.MediaError as e:
        raise OwnerError(str(e)) from e
    item = UnitMedia.objects.create(unit=claim.unit, claim=claim, kind=kind, uploaded_by=user, caption=caption[:120], **data)
    with rls.platform_context():
        for org_id in _serving_org_ids(claim.unit):
            notify_org(org_id, "owner_media_added", {"unit_id": str(claim.unit_id), "kind": kind})
    return item


def delete_media(item: UnitMedia, *, user) -> None:
    item.deleted_at = timezone.now()
    item.save(update_fields=["deleted_at"])
    audit(user, "owner.media_deleted", item.unit, {"media": str(item.pk)})


def flat_media(unit, *, kinds=("photo", "video")):
    return UnitMedia.objects.filter(unit=unit, kind__in=kinds, deleted_at__isnull=True).order_by("kind", "created_at")


def can_view_media(item: UnitMedia, user) -> bool:
    if user.is_staff:
        return True
    if OwnershipClaim.objects.filter(unit=item.unit, user=user, status__in=ACTIVE_CLAIM).exists():
        return item.kind != "document" or item.uploaded_by_id == user.pk
    if item.kind == "document":
        return False
    m_ = getattr(user, "active_membership", None)
    if m_ is None:
        return False
    return Listing.objects.filter(org_id=m_.org_id, unit=item.unit, archived_at__isnull=True, withdrawn_by_owner=False).exists()


# --- brokers: who serves the flat, nearby brokers, invite, allow / withdraw -----------------------------


def _serving_org_ids(unit) -> set:
    return set(Listing.objects.filter(unit=unit, archived_at__isnull=True, withdrawn_by_owner=False).values_list("org_id", flat=True))


def _contact(org) -> str:
    """The firm's business number: its principal's mobile (shared only with the flat's owner)."""
    p = Membership.objects.filter(org=org, role=Membership.Role.PRINCIPAL, active=True).select_related("user").first()
    return p.user.phone if p else ""


def flat_view(claim: OwnershipClaim) -> dict:
    """OWN-03: read-only status and 'Currently serviced by …' for the owner."""
    unit = claim.unit
    with rls.platform_context():
        statuses = [{"txn_type": s.txn_type, "state": s.state, "label": s.label} for s in UnitStatus.objects.filter(unit=unit)]
        listings = Listing.objects.filter(unit=unit, archived_at__isnull=True).select_related("org").order_by("created_at")
        brokers: dict = {}
        for l in listings:
            b = brokers.setdefault(
                l.org_id,
                {
                    "org_id": str(l.org_id),
                    "name": l.org.name,
                    "contact": _contact(l.org),
                    "rating": float(l.org.rating_bayes),
                    "rating_count": l.org.rating_count,
                    "since": l.created_at.isoformat(),
                    "owner_appointed": False,
                    "allowed": True,
                    "asked_back": "",
                },
            )
            b["owner_appointed"] |= l.origin == Listing.Origin.OWNER_INVITE
            b["allowed"] &= not l.withdrawn_by_owner
        for w in OwnerWithdrawal.objects.filter(unit=unit, active=True).select_related("org"):
            b = brokers.setdefault(
                w.org_id,
                {
                    "org_id": str(w.org_id),
                    "name": w.org.name,
                    "contact": _contact(w.org),
                    "rating": float(w.org.rating_bayes),
                    "rating_count": w.org.rating_count,
                    "since": w.created_at.isoformat(),
                    "owner_appointed": False,
                },
            )
            b.update(allowed=False, asked_back=w.ask_note if w.asked_at else "")
        invites = [
            {"id": str(i.pk), "org_id": str(i.org_id), "name": i.org.name, "state": i.state, "sent_at": i.created_at.isoformat()}
            for i in OwnerInvite.objects.filter(unit=unit, owner=claim.user, state=OwnerInvite.State.PENDING).select_related("org")
        ]
    return {"statuses": statuses, "brokers": list(brokers.values()), "invites": invites}


def brokers_nearby(claim: OwnershipClaim) -> list[dict]:
    """OWN-01: verified brokers who work where the flat is: service area covers it, or office within 5 km."""
    point = claim.unit.building.location
    with rls.platform_context():
        serving = _serving_org_ids(claim.unit)
        withdrawn = set(OwnerWithdrawal.objects.filter(unit=claim.unit, active=True).values_list("org_id", flat=True))
        orgs = (
            BrokerOrg.objects.filter(verification_status="verified")
            .filter(Q(service_areas__area__intersects=point) | Q(office_location__distance_lte=(point, D(m=NEARBY_M))))
            .distinct()
            .order_by("-rating_bayes", "-rating_count", "name")[:30]
        )
        return [
            {
                "org_id": str(o.pk),
                "name": o.name,
                "rating": float(o.rating_bayes),
                "rating_count": o.rating_count,
                "closures": o.closures,
                "median_response_min": round(o.median_response_s / 60) if o.median_response_s else None,
                "rera_verified": bool(o.rera_verified_at),
                "serving": o.pk in serving,
                "withdrawn": o.pk in withdrawn,
            }
            for o in orgs
        ]


@transaction.atomic
def invite(claim: OwnershipClaim, org: BrokerOrg, *, allow: bool, user) -> OwnerInvite:
    """OWN-02: nothing reaches a broker until the owner ticks 'Allow this broker to handle my property'."""
    if not allow:
        raise OwnerError("Tick “Allow this broker to handle my property” first")
    unit = claim.unit
    with rls.platform_context():
        if org.pk in _serving_org_ids(unit):
            raise OwnerError(f"{org.name} already handles this flat")
        _set_allowed(unit, org, True, owner=user)  # inviting a broker the owner had removed means allowing them again
        inv = OwnerInvite.objects.filter(unit=unit, org=org, state=OwnerInvite.State.PENDING).first()
        if inv is None:
            inv = OwnerInvite.objects.create(
                unit=unit, org=org, owner=user, txn_type=claim.terms.get("txn_type", "RENT"), terms=claim.terms, allowed_at=timezone.now()
            )
        notify_org(org.pk, "owner_invite", {"invite_id": str(inv.pk), "society": unit.building.society.canonical_name})
    audit(user, "owner.broker_invited", unit, {"org": str(org.pk), "allowed_at": inv.allowed_at.isoformat()})
    return inv


def _set_allowed(unit, org, allowed: bool, *, owner, reason: str = "") -> None:
    w = OwnerWithdrawal.objects.filter(unit=unit, org=org, active=True).first()
    if allowed:
        if w:
            w.active, w.reinstated_at = False, timezone.now()
            w.save(update_fields=["active", "reinstated_at"])
            Listing.objects.filter(unit=unit, org=org, archived_at__isnull=True).update(withdrawn_by_owner=False)
            notify_org(org.pk, "owner_reinstated", {"unit_id": str(unit.pk), "society": unit.building.society.canonical_name})
        return
    if w is None:
        OwnerWithdrawal.objects.create(unit=unit, org=org, owner=owner, reason=reason[:200])
    Listing.objects.filter(unit=unit, org=org, archived_at__isnull=True).update(withdrawn_by_owner=True)
    OwnerInvite.objects.filter(unit=unit, org=org, state=OwnerInvite.State.PENDING).update(state=OwnerInvite.State.CANCELLED)
    notify_org(org.pk, "owner_withdrew", {"unit_id": str(unit.pk), "society": unit.building.society.canonical_name})


@transaction.atomic
def set_allowed(claim: OwnershipClaim, org: BrokerOrg, allowed: bool, *, user, reason: str = "") -> None:
    """The owner's tick decides who represents the flat, for invited and self-added brokers alike (D14)."""
    with rls.platform_context():
        _set_allowed(claim.unit, org, allowed, owner=user, reason=reason)
    audit(user, "owner.broker_allowed" if allowed else "owner.broker_withdrawn", claim.unit, {"org": str(org.pk), "reason": reason[:200]})


def review_broker(claim: OwnershipClaim, org: BrokerOrg, *, stars, tags=(), text="", user):
    from apps.reviews.models import Interaction, Review
    from apps.reviews.services import submit

    with rls.platform_context():
        listing = Listing.objects.filter(unit=claim.unit, org=org).order_by("-created_at").first()
        if listing is None:
            raise OwnerError("You can review brokers who have handled this flat")
        inter, _ = Interaction.objects.get_or_create(
            kind=Interaction.Kind.OWNER_REPRESENTATION,
            ref_type="inventory.listing",
            ref_id=listing.pk,
            defaults={"org": org, "owner_user": user, "occurred_at": timezone.now()},
        )
        return submit(inter, reviewer=user, direction=Review.Direction.O2B, stars=stars, tags=tags, text=text)


# --- broker side ------------------------------------------------------------------------------------------


@transaction.atomic
def accept_invite(inv: OwnerInvite, *, user) -> Listing:
    """INV-08: the owner's terms and contact become the broker's own listing, badged 'Owner-appointed'."""
    from apps.inventory.services import create_listing

    if inv.state != OwnerInvite.State.PENDING:
        raise OwnerError("This invitation is no longer open")
    t = inv.terms
    data = {
        "asking_rent": t.get("expected_rent") if inv.txn_type == "RENT" else None,
        "asking_price": t.get("expected_price") if inv.txn_type != "RENT" else None,
        "deposit": t.get("deposit"),
        "available_from": date.fromisoformat(t["available_from"]) if t.get("available_from") else None,
    }
    listing, _ = create_listing(
        org=inv.org,
        user=user,
        unit=inv.unit,
        txn_type=inv.txn_type,
        data=data,
        owner_phone=inv.owner.phone,
        origin=Listing.Origin.OWNER_INVITE,
        source_type="owner_via_broker",
    )
    if listing.origin != Listing.Origin.OWNER_INVITE:  # the firm already had it: the owner has now appointed them
        listing.origin = Listing.Origin.OWNER_INVITE
        listing.save(update_fields=["origin"])
    inv.state, inv.listing, inv.responded_at = OwnerInvite.State.ACCEPTED, listing, timezone.now()
    inv.save(update_fields=["state", "listing", "responded_at"])
    notify_user(inv.owner, "owner_invite_accepted", {"org": inv.org.name, "unit_id": str(inv.unit_id)})
    return listing


def decline_invite(inv: OwnerInvite, *, user) -> None:
    if inv.state != OwnerInvite.State.PENDING:
        raise OwnerError("This invitation is no longer open")
    inv.state, inv.responded_at = OwnerInvite.State.DECLINED, timezone.now()
    inv.save(update_fields=["state", "responded_at"])
    notify_user(inv.owner, "owner_invite_declined", {"org": inv.org.name, "unit_id": str(inv.unit_id)})


def ask_owner_back(org, unit: Unit, *, note: str, user) -> OwnerWithdrawal:
    """After being removed, a broker can put things right and ask again; the owner decides."""
    w = OwnerWithdrawal.objects.filter(org=org, unit=unit, active=True).first()
    if w is None:
        raise OwnerError("The owner has not removed your firm from this flat")
    w.ask_note, w.asked_at = note.strip()[:300], timezone.now()
    w.save(update_fields=["ask_note", "asked_at"])
    notify_user(w.owner, "broker_asks_back", {"org": org.name, "unit_id": str(unit.pk), "note": w.ask_note})
    return w


def withdrawn_orgs(unit) -> set:
    return set(OwnerWithdrawal.objects.filter(unit=unit, active=True).values_list("org_id", flat=True))
