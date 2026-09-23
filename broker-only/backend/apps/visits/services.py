"""Site-visit planning and dispatch (VISIT-01..09) and offline sync (OFF-10/11)."""

from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.crm import services as crm
from apps.crm.models import CustomerInteraction
from apps.inventory.models import KeyCustody
from apps.orgs.models import Membership
from common import crypto, rls
from common.links import create_link, resolve_link
from common.models import ShareLink
from common.notify import notify_user, send_message, ws_send

from . import routing
from .models import SyncMutation, VisitPlan, VisitStop

CHECKIN_RADIUS_M = 200


class VisitError(Exception):
    pass


def _pt(listing):
    loc = listing.unit.location or listing.unit.building.location
    return (loc.x, loc.y)


@transaction.atomic
def create_plan(
    *,
    customer,
    listings,
    date,
    start_time,
    user,
    start_point=None,
    travel_mode="two_wheeler",
    dwell_min=15,
    requirement=None,
    optimise=True,
) -> VisitPlan:
    listings = list(listings)
    if not listings:
        raise VisitError("Add at least one flat")
    if any(l.org_id != customer.org_id for l in listings):
        raise VisitError("A visit plan can only include your own listings")
    plan = VisitPlan.objects.create(
        org_id=customer.org_id,
        customer=customer,
        requirement=requirement,
        date=date,
        start_time=start_time,
        start_point=start_point,
        travel_mode=travel_mode,
        dwell_min=dwell_min,
        created_by=user,
    )
    for i, l in enumerate(listings):
        VisitStop.objects.create(org_id=plan.org_id, plan=plan, seq=i + 1, listing=l)
    if optimise:
        optimise_route(plan)
    else:
        retime(plan)
    crm.log(customer, CustomerInteraction.Kind.VISIT, f"Visit plan for {date:%d %b}: {len(listings)} flats", user=user, ref=plan)
    return plan


def live_stops(plan):
    return list(plan.stops.filter(removed=False).select_related("listing__unit__building").order_by("seq"))


def optimise_route(plan: VisitPlan) -> VisitPlan:
    stops = live_stops(plan)
    start = (plan.start_point.x, plan.start_point.y) if plan.start_point else None
    order = routing.order_stops(start, [_pt(s.listing) for s in stops])
    for new_seq, idx in enumerate(order, start=1):
        stops[idx].seq = 1000 + new_seq  # two-phase to avoid transient duplicates
        stops[idx].save(update_fields=["seq"])
    for s in plan.stops.filter(seq__gte=1000):
        s.seq -= 1000
        s.save(update_fields=["seq"])
    plan.route_method = "local_2opt"
    return retime(plan)


def retime(plan: VisitPlan) -> VisitPlan:
    tz = timezone.get_current_timezone()
    t = timezone.make_aware(datetime.combine(plan.date, plan.start_time), tz)
    here = (plan.start_point.x, plan.start_point.y) if plan.start_point else None
    travel_total = 0
    for s in live_stops(plan):
        p = _pt(s.listing)
        if here:
            m = routing.travel_min(here, p, plan.travel_mode)
            t += timedelta(minutes=m)
            travel_total += m
        s.slot_start, s.slot_end = t, t + timedelta(minutes=plan.dwell_min)
        s.save(update_fields=["slot_start", "slot_end"])
        t, here = s.slot_end, p
    plan.total_travel_min = travel_total
    plan.save(update_fields=["route_method", "total_travel_min", "updated_at"])
    return plan


def key_conflicts(plan: VisitPlan) -> list[dict]:
    """VISIT-04: the same key needed by two plans at overlapping times, or keys with the owner/society office."""
    out = []
    for s in live_stops(plan):
        key = KeyCustody.objects.filter(listing=s.listing, to_ts__isnull=True).first()
        if key is None:
            out.append({"stop_id": str(s.pk), "issue": "no_key_recorded"})
        elif key.holder_type in ("owner", "society_office"):
            out.append({"stop_id": str(s.pk), "issue": f"key_with_{key.holder_type}"})
        if key and key.needs_handover:
            out.append({"stop_id": str(s.pk), "issue": "key_needs_handover"})
        clash = VisitStop.objects.filter(
            listing=s.listing,
            removed=False,
            slot_start__lt=s.slot_end,
            slot_end__gt=s.slot_start,
            plan__state__in=["draft", "shared", "customer_confirmed", "in_progress"],
            plan__date=plan.date,
        ).exclude(plan=plan)
        if clash.exists():
            out.append({"stop_id": str(s.pk), "issue": "same_flat_booked_in_another_plan_at_overlapping_time"})
    return out


@transaction.atomic
def assign(plan: VisitPlan, staff_user, *, stop_ids=None) -> int:
    if not Membership.objects.filter(user=staff_user, org_id=plan.org_id, active=True).exists():
        raise VisitError("That person is not part of your team")
    qs = plan.stops.filter(removed=False)
    if stop_ids:
        qs = qs.filter(pk__in=stop_ids)
    n = qs.update(assigned_staff=staff_user, staff_ack_at=None)
    _bump(plan, "visit_stop.assigned", actor=None)
    notify_user(
        staff_user,
        "visit_assigned",
        {"plan_id": str(plan.pk), "date": plan.date.isoformat(), "stops": n},
        realtime_event="visit_stop.assigned",
    )
    return n


def acknowledge(plan: VisitPlan, staff_user) -> int:
    return plan.stops.filter(assigned_staff=staff_user, staff_ack_at__isnull=True).update(staff_ack_at=timezone.now())


def share_with_customer(plan: VisitPlan, *, user) -> str:
    """VISIT-02 / OFF-04: works for app and offline customers alike."""
    crm.ensure_can_message(plan.customer)
    link, token = create_link(
        ShareLink.Purpose.VISIT_PLAN, plan, hours=24 * 7, max_uses=10_000, recipient_phone_hash=plan.customer.phone_hash
    )
    send_message(
        plan.customer.phone,
        "visit_plan_shared",
        {
            "date": plan.date.strftime("%a %d %b").replace(" 0", " "),
            "stops": len(live_stops(plan)),
            "url": f"{settings.OB_PUBLIC_BASE_URL}/v/{token}",
        },
        phone_hash=plan.customer.phone_hash,
    )
    if plan.state == VisitPlan.State.DRAFT:
        plan.state = VisitPlan.State.SHARED
        plan.save(update_fields=["state"])
    return token


def public_plan_view(token: str) -> dict:
    link = resolve_link(token, ShareLink.Purpose.VISIT_PLAN, consume=False)
    with rls.platform_context():
        plan = VisitPlan.objects.select_related("customer").get(pk=link.target_id)
        confirmed = plan.state in (VisitPlan.State.CUSTOMER_CONFIRMED, VisitPlan.State.IN_PROGRESS, VisitPlan.State.COMPLETED)
        stops = []
        for s in live_stops(plan):
            b = s.listing.unit.building
            stops.append(
                {
                    "seq": s.seq,
                    "society": b.society.canonical_name,
                    "building": b.name,
                    # Exact flat number only after the customer confirms (VISIT-02).
                    "flat": s.listing.unit.unit_no if confirmed else None,
                    "bhk": float(s.listing.unit.bhk),
                    "rent_or_price": s.listing.price,
                    "slot_start": s.slot_start.isoformat() if s.slot_start else None,
                    "location": {"lat": b.location.y, "lng": b.location.x},
                    "staff": s.assigned_staff.display_name if s.assigned_staff else None,
                }
            )
        return {"date": plan.date.isoformat(), "state": plan.state, "stops": stops, "version": plan.version, "org_id": plan.org_id}


def customer_confirms(token: str, *, slot: datetime | None = None) -> VisitPlan:
    link = resolve_link(token, ShareLink.Purpose.VISIT_PLAN, consume=False)
    with rls.platform_context():
        plan = VisitPlan.objects.get(pk=link.target_id)
        if slot:
            plan.customer_proposed_slot = slot
            crm.log(plan.customer, CustomerInteraction.Kind.LINK_OPENED, f"Customer proposed {slot:%d %b %H:%M}")
        else:
            plan.state = VisitPlan.State.CUSTOMER_CONFIRMED
            crm.log(plan.customer, CustomerInteraction.Kind.LINK_OPENED, "Customer confirmed the visit plan")
        plan.save(update_fields=["customer_proposed_slot", "state"])
        ws_send(f"broker.{plan.org_id}", "visit_plan.updated", {"plan_id": str(plan.pk), "state": plan.state})
    return plan


def notify_owners(plan: VisitPlan) -> int:
    """VISIT-05: tell owners (who may not have the app) about scheduled visits, with an acknowledge link."""
    n = 0
    for s in live_stops(plan):
        phone = s.listing.owner_phone
        if not phone or s.owner_notice != VisitStop.OwnerNotice.NOT_REQUIRED:
            continue
        link, token = create_link(ShareLink.Purpose.VISIT_NOTICE, s, hours=48)
        send_message(
            phone,
            "visit_notice",
            {
                "flat": str(s.listing.unit),
                "when": _human_when(s.slot_start, plan.date),
                "url": f"{settings.OB_PUBLIC_BASE_URL}/o/{token}",
            },
            phone_hash=crypto.phone_hash(phone),
        )
        s.owner_notice = VisitStop.OwnerNotice.SENT
        s.save(update_fields=["owner_notice"])
        n += 1
    return n


def _human_when(slot, day) -> str:
    """Message text is read by people: India time, in words ("Fri 25 Sep, 11:00 AM")."""
    if slot:
        return timezone.localtime(slot).strftime("%a %d %b, %I:%M %p").replace(" 0", " ")
    return day.strftime("%a %d %b")


def owner_acknowledges(token: str, ok: bool) -> VisitStop:
    link = resolve_link(token, ShareLink.Purpose.VISIT_NOTICE, consume=True)
    with rls.platform_context():
        s = VisitStop.objects.get(pk=link.target_id)
        s.owner_notice = VisitStop.OwnerNotice.ACKNOWLEDGED if ok else VisitStop.OwnerNotice.DECLINED
        s.save(update_fields=["owner_notice"])
        ws_send(
            f"broker.{s.org_id}", "visit_plan.updated", {"plan_id": str(s.plan_id), "stop_id": str(s.pk), "owner_notice": s.owner_notice}
        )
    return s


# --- live changes (VISIT-06) -------------------------------------------------


@transaction.atomic
def add_stop(plan: VisitPlan, listing, *, position=None) -> VisitStop:
    if listing.org_id != plan.org_id:
        raise VisitError("Only your own listings")
    stops = live_stops(plan)
    pos = len(stops) + 1 if position is None else max(1, min(position, len(stops) + 1))
    for s in reversed(stops):
        if s.seq >= pos:
            s.seq += 1
            s.save(update_fields=["seq"])
    stop = VisitStop.objects.create(
        org_id=plan.org_id, plan=plan, seq=pos, listing=listing, assigned_staff=stops[0].assigned_staff if stops else None
    )
    retime(plan)
    _bump(plan, "visit_plan.updated")
    return stop


@transaction.atomic
def remove_stop(plan: VisitPlan, stop: VisitStop) -> None:
    stop.removed = True
    stop.save(update_fields=["removed"])
    for i, s in enumerate(live_stops(plan), start=1):
        if s.seq != i:
            s.seq = i
            s.save(update_fields=["seq"])
    retime(plan)
    _bump(plan, "visit_plan.updated")


@transaction.atomic
def reorder(plan: VisitPlan, stop_ids: list) -> None:
    stops = {str(s.pk): s for s in live_stops(plan)}
    if set(map(str, stop_ids)) != set(stops):
        raise VisitError("Give every stop exactly once")
    for i, sid in enumerate(stop_ids, start=1):
        stops[str(sid)].seq = 1000 + i
        stops[str(sid)].save(update_fields=["seq"])
    for s in plan.stops.filter(seq__gte=1000):
        s.seq -= 1000
        s.save(update_fields=["seq"])
    retime(plan)
    _bump(plan, "visit_plan.updated")


def _bump(plan: VisitPlan, event: str, actor=None):
    plan.version += 1
    plan.save(update_fields=["version"])
    payload = {"plan_id": str(plan.pk), "version": plan.version}
    ws_send(f"visit_plan.{plan.pk}", event, payload)
    for staff_id in plan.stops.filter(removed=False, assigned_staff__isnull=False).values_list("assigned_staff_id", flat=True).distinct():
        ws_send(f"user.{staff_id}", event, payload)


# --- at the flat (VISIT-07) --------------------------------------------------


def check_in(stop: VisitStop, *, lat=None, lng=None, at=None) -> VisitStop:
    stop.checkin_at = at or timezone.now()
    if lat is not None and lng is not None:
        stop.checkin_distance_m = round(routing.haversine_m((float(lng), float(lat)), _pt(stop.listing)))
    stop.save(update_fields=["checkin_at", "checkin_distance_m"])
    if stop.plan.state in (VisitPlan.State.CUSTOMER_CONFIRMED, VisitPlan.State.SHARED, VisitPlan.State.DRAFT):
        stop.plan.state = VisitPlan.State.IN_PROGRESS
        stop.plan.save(update_fields=["state"])
    return stop


@transaction.atomic
def record_outcome(stop: VisitStop, outcome: str, *, user, reasons=(), note="", at=None) -> VisitStop:
    if outcome not in VisitStop.Outcome.values:
        raise VisitError("Unknown outcome")
    stop.outcome = outcome
    stop.reject_reasons = list(reasons)
    stop.feedback_note = note[:500]
    stop.checkout_at = at or timezone.now()
    stop.save(update_fields=["outcome", "reject_reasons", "feedback_note", "checkout_at"])
    crm.log(stop.plan.customer, CustomerInteraction.Kind.VISIT, f"{stop.listing.unit}: {outcome.replace('_', ' ')}", user=user, ref=stop)
    if outcome == VisitStop.Outcome.ALREADY_LET:
        # Visit evidence feeds the master status (Data Model §4 rule 3).
        from apps.status import services as st

        st.report(
            stop.listing.unit,
            stop.listing.txn_type,
            "LET" if stop.listing.txn_type == "RENT" else "SOLD",
            st.Actor("visit_feedback", org=stop.listing.org, user=user),
            reason="found let at site visit",
        )
    if not stop.plan.stops.filter(removed=False, outcome="").exists():
        complete_plan(stop.plan)
    return stop


def complete_plan(plan: VisitPlan) -> None:
    """Completion creates a verified interaction, which unlocks reviews (REV-01, OFF-08)."""
    from apps.reviews.services import visit_completed

    plan.state = VisitPlan.State.COMPLETED
    plan.save(update_fields=["state"])
    if plan.stops.filter(removed=False, checkin_at__isnull=False).exists():
        visit_completed(plan)


# --- offline sync (OFF-10/11) -------------------------------------------------


def apply_mutations(*, org_id, user, device_id: str, mutations: list[dict]) -> list[dict]:
    """Apply queued field-app mutations exactly once.

    Conflict rules: server wins for plan structure (a removed stop cannot be updated);
    the device wins for what it observed (check-in time, outcome).
    """
    out = []
    for m in mutations:
        key = str(m["idempotency_key"])[:64]
        prior = SyncMutation.objects.filter(idempotency_key=key).first()
        if prior:
            out.append({"idempotency_key": key, "result": "duplicate", "detail": prior.detail})
            continue
        with transaction.atomic():
            result, detail = _apply_one(org_id, user, m)
            SyncMutation.objects.create(
                idempotency_key=key,
                org_id=org_id,
                user=user,
                device_id=device_id[:64],
                entity=m.get("entity", "")[:30],
                payload=m,
                client_ts=m.get("client_ts") or timezone.now(),
                result=result,
                detail=detail,
            )
        out.append({"idempotency_key": key, "result": result, "detail": detail})
    return out


def _apply_one(org_id, user, m) -> tuple[str, dict]:
    stop = VisitStop.objects.filter(pk=m.get("stop_id"), org_id=org_id).select_related("plan", "listing__unit__building").first()
    if stop is None:
        return "conflict", {"reason": "stop_not_found"}
    if stop.removed:
        return "conflict", {"reason": "stop_removed_by_broker", "plan_version": stop.plan.version}
    membership = Membership.objects.filter(user=user, org_id=org_id, active=True).first()
    if membership and membership.role == Membership.Role.STAFF and stop.assigned_staff_id != user.pk:
        return "conflict", {"reason": "not_assigned_to_you"}
    at = m.get("client_ts")
    if isinstance(at, str):
        at = datetime.fromisoformat(at)
    entity = m.get("entity")
    if entity == "checkin":
        check_in(stop, lat=m.get("lat"), lng=m.get("lng"), at=at)
    elif entity == "outcome":
        record_outcome(stop, m["outcome"], user=user, reasons=m.get("reasons", []), note=m.get("note", ""), at=at)
    elif entity == "ack":
        acknowledge(stop.plan, user)
    else:
        return "conflict", {"reason": "unknown_entity"}
    return "applied", {"stop_id": str(stop.pk)}
