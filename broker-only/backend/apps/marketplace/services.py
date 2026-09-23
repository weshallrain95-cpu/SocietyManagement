"""Marketplace: enquiry -> real-time broadcast -> proposals -> accept (MKT-01..11)."""
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Point
from django.db import transaction
from django.utils import timezone

from apps.crm import services as crm
from apps.crm.models import Customer, CustomerInteraction
from apps.matching.engine import run as run_match
from apps.orgs.models import BrokerOrg, ServiceArea
from common import rls
from common.events import emit
from common.notify import notify_org, notify_user, queue_for_admin

from . import presence
from .models import Enquiry, EnquiryDelivery, Proposal

FREE_PROPOSALS_PER_MONTH = {"free": 20, "pro": 10_000, "agency": 100_000}
BANNED_PHRASES = ("community only", "no people from", "only people from", "only family of")


class MarketError(Exception):
    pass


def circle(center: Point, metres: int) -> MultiPolygon:
    p = center.transform(32643, clone=True).buffer(metres, quadsegs=12)
    p.transform(4326)
    return MultiPolygon(p, srid=4326)


def summarise(e) -> str:
    """'2 BHK on rent, urgent, around Dhokali (3 km), up to ₹25,000, pets, gas stove + kitchen cabinet'."""
    bhk = f"{e.bhk_min:g}" if e.bhk_min == e.bhk_max else f"{e.bhk_min:g}–{e.bhk_max:g}"
    kind = {"RENT": "on rent", "SALE_NEW": "to buy (new)", "SALE_RESALE": "to buy (resale)"}[e.txn_type]
    parts = [f"{bhk} BHK {kind}"]
    if e.urgency == "urgent":
        parts.append("urgent")
    parts.append(f"around {e.area_label or 'the chosen area'} ({e.radius_m / 1000:g} km)")
    parts.append(f"up to ₹{e.budget_max:,}" + ("/month" if e.txn_type == "RENT" else ""))
    needs = [k.replace("_", " ") for k in (e.house_rule_needs or {})]
    musts = [k.replace("furn_", "").replace("_", " ") for k in (e.must_haves or {})]
    if needs:
        parts.append(", ".join(needs))
    if musts:
        parts.append(" + ".join(musts))
    return ", ".join(parts)[:300]


def moderate(text: str) -> str:
    """Free text may not set conditions about who people are (BRD §10.2)."""
    low = (text or "").lower()
    if any(p in low for p in BANNED_PHRASES):
        raise MarketError("Please describe the home and how it will be used, not who may live there.")
    return (text or "")[:500]


@transaction.atomic
def create_enquiry(user, data: dict) -> Enquiry:
    cfg = settings.OB_MARKET
    if Enquiry.objects.filter(customer_user=user, state__in=["open", "in_progress"]).count() >= cfg["max_open_enquiries_per_customer"]:
        raise MarketError(f"You can have at most {cfg['max_open_enquiries_per_customer']} open enquiries.")
    data = dict(data)
    data["notes"] = moderate(data.get("notes", ""))
    e = Enquiry(customer_user=user, expires_at=timezone.now() + timedelta(days=cfg["enquiry_ttl_days"]), **data)
    e.summary_text = summarise(e)
    e.save()
    emit("enquiry.created", enquiry_id=e.pk)
    return e


class _EnquiryAsRequirement:
    """Adapter so the matcher can score an enquiry against a broker's listings."""

    def __init__(self, e: Enquiry):
        self.txn_type, self.bhk_min, self.bhk_max = e.txn_type, e.bhk_min, e.bhk_max
        self.budget_min, self.budget_max = e.budget_min, e.budget_max
        self.search_area = circle(e.center, e.radius_m)
        self.must_haves, self.house_rule_needs = e.must_haves, e.house_rule_needs
        self.max_station_distance_m, self.occupants = e.max_station_distance_m, e.occupants
        self.nice_to_haves, self.pk = {}, None


def eligible_orgs(e: Enquiry):
    area = circle(e.center, e.radius_m)
    org_ids = (
        ServiceArea.objects.filter(area__intersects=area)
        .filter(org__verification_status=BrokerOrg.Verification.VERIFIED, org__txn_types__contains=[e.txn_type])
        .values_list("org_id", flat=True)
        .distinct()
    )
    orgs = list(BrokerOrg.objects.filter(pk__in=list(org_ids)).order_by("-rating_bayes", "median_response_s"))
    cap = settings.OB_MARKET["broadcast_cap"]
    if len(orgs) > cap:
        # 80% by quality, 20% random slice so new brokers get a chance.
        import random

        top, rest = orgs[: int(cap * 0.8)], orgs[int(cap * 0.8):]
        orgs = top + random.sample(rest, cap - len(top))
    return orgs


def broadcast(enquiry_id) -> int:
    """Runs in platform context (outbox handler). Brokers see only their own match COUNT, never others'."""
    e = Enquiry.objects.get(pk=enquiry_id)
    if e.state != Enquiry.State.OPEN:
        return 0
    req = _EnquiryAsRequirement(e)
    n = 0
    for org in eligible_orgs(e):
        count = len(run_match(req, org_id=org.pk))
        online = presence.is_online(org.pk)
        _, created = EnquiryDelivery.objects.get_or_create(
            enquiry=e, org=org, defaults={"channel": "ws" if online else "push", "match_count": count}
        )
        if not created:
            continue
        notify_org(org.pk, "enquiry_new", {
            "enquiry_id": str(e.pk), "summary": e.summary_text, "match_count": count, "txn_type": e.txn_type,
            "expires_at": e.expires_at.isoformat(), "urgency": e.urgency,
        }, realtime_event="enquiry.new")
        n += 1
    Enquiry.objects.filter(pk=e.pk).update(n_recipients=n)
    return n


def _proposals_this_month(org) -> int:
    start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return Proposal.objects.filter(org=org, created_at__gte=start).count()


@transaction.atomic
def send_proposal(org, user, enquiry: Enquiry, *, brokerage_terms: str, message: str = "", earliest_slot=None) -> Proposal:
    if not org.is_verified:
        raise MarketError("Your broker account is pending verification.")
    if enquiry.state not in (Enquiry.State.OPEN, Enquiry.State.IN_PROGRESS) or enquiry.expires_at < timezone.now():
        raise MarketError("This enquiry is closed.")
    delivery = EnquiryDelivery.objects.filter(enquiry=enquiry, org=org).first()
    if delivery is None:
        raise MarketError("This enquiry was not sent to you.")
    if _proposals_this_month(org) >= FREE_PROPOSALS_PER_MONTH.get(org.plan_code, 20):
        raise MarketError("You have used this month's responses on your plan.")
    p, created = Proposal.objects.get_or_create(
        enquiry=enquiry, org=org,
        defaults={
            "sent_by": user, "brokerage_terms": brokerage_terms[:200], "message": moderate(message),
            "match_count": delivery.match_count, "earliest_slot": earliest_slot,
            "response_s": int((timezone.now() - enquiry.created_at).total_seconds()),
        },
    )
    if not created:
        raise MarketError("You have already responded to this enquiry.")
    notify_user(enquiry.customer_user, "proposal_new", {"enquiry_id": str(enquiry.pk), "proposal_id": str(p.pk), "broker": org.name},
                realtime_event="proposal.new")
    emit("proposal.sent", org_id=org.pk)
    return p


@transaction.atomic
def accept_proposal(user, proposal: Proposal) -> Proposal:
    e = proposal.enquiry
    if e.customer_user_id != user.pk:
        raise MarketError("Not your enquiry")
    if proposal.state != Proposal.State.SENT:
        raise MarketError("This proposal can no longer be accepted")
    limit = settings.OB_MARKET["max_accepted_proposals"]
    if e.proposals.filter(state=Proposal.State.ACCEPTED).count() >= limit:
        raise MarketError(f"You can work with up to {limit} brokers per enquiry.")
    proposal.state = Proposal.State.ACCEPTED
    proposal.save(update_fields=["state"])
    e.state = Enquiry.State.IN_PROGRESS
    e.save(update_fields=["state"])
    # The broker gets the customer (with consent given in-app) and the requirement in their CRM.
    with rls.org_context(proposal.org_id):
        cust, _ = crm.capture_customer(org=proposal.org, user=None, phone=user.phone, name=user.display_name, source=Customer.Source.MARKETPLACE)
        cust.platform_user = user
        cust.consent_state = Customer.Consent.APP
        cust.consent_evidence = {"method": "app", "enquiry": str(e.pk), "at": timezone.now().isoformat()}
        cust.save(update_fields=["platform_user", "consent_state", "consent_evidence"])
        crm.add_requirement(cust, {
            "enquiry": e, "txn_type": e.txn_type, "property_types": e.property_types, "bhk_min": e.bhk_min,
            "bhk_max": e.bhk_max, "budget_min": e.budget_min, "budget_max": e.budget_max,
            "search_area": circle(e.center, e.radius_m), "must_haves": e.must_haves, "house_rule_needs": e.house_rule_needs,
            "max_station_distance_m": e.max_station_distance_m, "move_in_by": e.move_in_by, "occupants": e.occupants, "notes": e.notes,
        })
        crm.log(cust, CustomerInteraction.Kind.SYSTEM, "Marketplace enquiry accepted your proposal", ref=proposal)
    notify_org(proposal.org_id, "proposal_accepted", {"proposal_id": str(proposal.pk), "customer_id": str(cust.pk)},
               realtime_event="proposal.accepted")
    if e.proposals.filter(state=Proposal.State.ACCEPTED).count() >= limit:
        for other in e.proposals.filter(state=Proposal.State.SENT):
            other.state = Proposal.State.DECLINED
            other.save(update_fields=["state"])
            notify_org(other.org_id, "enquiry_closed", {"enquiry_id": str(e.pk)}, realtime_event="enquiry.closed")
    return proposal


def close_enquiry(user, e: Enquiry, state=Enquiry.State.CANCELLED) -> Enquiry:
    if e.customer_user_id != user.pk:
        raise MarketError("Not your enquiry")
    e.state = state
    e.save(update_fields=["state"])
    for org_id in e.deliveries.values_list("org_id", flat=True):
        notify_org(org_id, "enquiry_closed", {"enquiry_id": str(e.pk)}, realtime_event="enquiry.closed")
    return e


def report_fake(org, e: Enquiry, reason: str):
    """MKT-10: brokers can flag spam enquiries; ops refunds credits on validation."""
    queue_for_admin("reported_enquiry", e, f"{org.name} reported enquiry: {reason[:200]}", {"org_id": str(org.pk)})


def expire_enquiries(now=None) -> int:
    now = now or timezone.now()
    return Enquiry.objects.filter(state__in=["open", "in_progress"], expires_at__lt=now).update(state=Enquiry.State.EXPIRED)
