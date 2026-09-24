"""Co-broking services (D17). See models.py for the rules."""

import math
import re
from urllib.parse import quote

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils import timezone

from apps.crm.broadcasts import _inr, flat_summary
from apps.crm.models import Requirement
from apps.inventory.models import Listing
from apps.masterdata.models import Locality
from apps.orgs.models import Membership
from common import crypto, rls
from common.notify import notify_org
from common.people_import import clean_phone, read_people, text

from .models import FellowBroker, TradeBlast, TradeDelivery, TradeReply

DEFAULT_RADIUS_KM = 3.0
MAX_RADIUS_KM = 50.0
MAX_FLATS = 10
MAX_TEXT = 1000

IMPORT_COLUMNS = {
    "name": ("name", "broker", "broker name", "contact", "contact name", "person"),
    "firm": ("firm", "agency", "company", "office", "firm name", "agency name"),
    "phone": ("phone", "mobile", "mobile no", "mobile number", "number", "contact no", "contact number", "whatsapp", "phone no"),
    "address": ("address", "office address"),
    "area": ("area", "locality", "location", "place"),
    "notes": ("notes", "remarks", "comment"),
}


class TradeError(Exception):
    pass


# --- the fellow-broker list ---------------------------------------------------------------------


def guess_locality(*texts: str) -> Locality | None:
    def fold(t):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).split())

    hay = f" {fold(' '.join(t for t in texts if t))} "
    if not hay.strip():
        return None
    best, best_len = None, 0
    for loc in Locality.objects.all():
        key = fold(loc.name)
        if key and f" {key} " in hay and len(key) > best_len:
            best, best_len = loc, len(key)
    return best


def platform_firm(phone_hash: str, org):
    """The fellow broker's firm on Only Broker, if their number belongs to an active broker member."""
    m = (
        Membership.objects.filter(user__phone_hash=phone_hash, active=True)
        .exclude(org=org)
        .select_related("org")
        .order_by("created_at")
        .first()
    )
    return m.org if m else None


@transaction.atomic
def save_contact(org, *, name: str, phone: str, firm="", address="", area="", locality=None, lat=None, lng=None, notes="", source="manual"):
    e164 = clean_phone(phone)
    if not e164:
        raise TradeError("Enter a valid mobile number")
    name = text(name, 120) or text(firm, 120)
    if not name:
        raise TradeError("Enter the broker's name")
    ph = crypto.phone_hash(e164)
    if locality is None:
        locality = guess_locality(area, address)
    c = FellowBroker.objects.filter(org=org, phone_hash=ph).first()
    created = c is None
    if created:
        c = FellowBroker(org=org, phone_hash=ph, phone_enc=crypto.encrypt(e164), source=source)
    c.name = name if (created or source == "manual") else (c.name or name)
    for field, val, limit in (("firm", firm, 160), ("address", address or area, 300), ("notes", notes, 300)):
        v = text(val, limit)
        if v and (source == "manual" or not getattr(c, field)):
            setattr(c, field, v)
    if locality is not None and (source == "manual" or c.locality_id is None):
        c.locality = locality
    if lat is not None and lng is not None:
        c.location = Point(float(lng), float(lat), srid=4326)
    c.platform_org = platform_firm(ph, org)
    c.active = True
    c.save()
    return c, created


def import_contacts(org, *, filename: str, content: bytes) -> dict:
    rows = read_people(filename, content, IMPORT_COLUMNS)
    added = updated = 0
    skipped = []
    for i, r in enumerate(rows, start=1):
        try:
            _, created = save_contact(
                org,
                name=r.get("name") or "",
                phone=r.get("phone") or "",
                firm=r.get("firm") or "",
                address=r.get("address") or "",
                area=r.get("area") or "",
                notes=r.get("notes") or "",
                source=FellowBroker.Source.IMPORT,
            )
        except TradeError as e:
            skipped.append({"row": i, "reason": str(e), "text": text(r.get("name") or r.get("raw") or r.get("phone"), 60)})
            continue
        added += created
        updated += not created
    return {"added": added, "updated": updated, "skipped": skipped[:200], "skipped_count": len(skipped)}


def contact_json(c: FellowBroker, distance_km=None) -> dict:
    return {
        "id": str(c.pk),
        "name": c.name,
        "firm": c.firm,
        "phone": c.phone,
        "address": c.address,
        "locality": c.locality.name if c.locality_id else None,
        "has_location": _where(c) is not None,
        "on_platform": c.platform_org_id is not None,
        "notes": c.notes,
        "distance_km": round(distance_km, 1) if distance_km is not None else None,
    }


# --- who a blast reaches ------------------------------------------------------------------------


def _where(c: FellowBroker):
    if c.location is not None:
        return c.location
    if c.locality_id:
        return c.locality.centroid
    if c.platform_org_id and c.platform_org.office_location is not None:
        return c.platform_org.office_location
    return None


def _km(a, b) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a.y, a.x, b.y, b.x))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def centres(listings=(), requirement: Requirement | None = None) -> list:
    pts = [li.unit.effective_location for li in listings]
    if requirement is not None:
        pts += [loc.centroid for loc in requirement.localities.all()]
        if not pts and requirement.search_area is not None:
            pts.append(requirement.search_area.centroid)
    return [p for p in pts if p is not None]


def audience(org, *, centre_points, scope="radius", radius_km=DEFAULT_RADIUS_KM, contact_ids=None) -> list[dict]:
    """Every fellow broker, nearest first, with `selected` set by the chosen scope.

    scope: "radius" (in and around the flats, radius widened by the broker), "all", or "selected" (ticked names).
    """
    radius_km = max(0.5, min(float(radius_km or DEFAULT_RADIUS_KM), MAX_RADIUS_KM))
    chosen = {str(x) for x in (contact_ids or [])}
    out = []
    for c in FellowBroker.objects.filter(org=org, active=True).select_related("locality", "platform_org"):
        where = _where(c)
        d = min((_km(where, p) for p in centre_points), default=None) if where is not None else None
        in_radius = d is not None and d <= radius_km
        selected = {"all": True, "selected": str(c.pk) in chosen}.get(scope, in_radius)
        out.append({"contact": c, "distance_km": d, "in_radius": in_radius, "selected": selected})
    out.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"] or 0, r["contact"].name.lower()))
    return out


def counts(rows) -> dict:
    sel = [r for r in rows if r["selected"]]
    firms = {r["contact"].platform_org_id for r in sel if r["contact"].platform_org_id}
    return {
        "total": len(rows),
        "selected": len(sel),
        "in_app": len(firms),
        "whatsapp": sum(1 for r in sel if not r["contact"].platform_org_id),
        "no_location": sum(1 for r in rows if r["distance_km"] is None),
    }


# --- what goes out ------------------------------------------------------------------------------


def requirement_summary(req: Requirement) -> dict:
    lo, hi = float(req.bhk_min), float(req.bhk_max)

    def word(x):
        return "1 RK" if x == 0.5 else f"{x:g}"

    bhk = f"{word(lo)} BHK" if lo == hi else f"{word(lo)}–{word(hi)} BHK"
    rent = req.txn_type == "RENT"
    return {
        "txn_type": req.txn_type,
        "bhk": bhk,
        "localities": [loc.name for loc in req.localities.all()],
        "budget_label": f"up to {_inr(req.budget_max)}{'/month' if rent else ''}",
        "move_in_by": req.move_in_by.isoformat() if req.move_in_by else None,
    }


def _flat_line(f: dict) -> str:
    what = "for rent" if f["txn_type"] == "RENT" else "for sale"
    price = f" — {f['price_label']}" if f.get("price_label") else ""
    when = f" (from {f['available_from']})" if f.get("available_from") else ""
    return f"• {f['bhk']} {what}, {f['society']}, {f['locality']}{price}{when}"


def default_text(kind, *, org, user, items) -> str:
    who = f"{user.display_name or org.name} ({org.name}) {user.phone}" if user.display_name else f"{org.name} {user.phone}"
    if kind == TradeBlast.Kind.FLATS:
        head = "Ready flats available:" if len(items) > 1 else "Ready flat available:"
        return "\n".join([head, *(_flat_line(f) for f in items), f"Have a customer? Call {who}."])
    r = items[0]
    what = "for rent" if r["txn_type"] == "RENT" else "to buy"
    where = f" in {', '.join(r['localities'])}" if r["localities"] else ""
    when = f", move in by {r['move_in_by']}" if r.get("move_in_by") else ""
    return f"Wanted: {r['bhk']} {what}{where}, {r['budget_label']}{when}. Have one? Call {who}."


def whatsapp_link(phone_e164: str, message: str) -> str:
    return f"https://wa.me/{phone_e164.lstrip('+')}?text={quote(message)}"


def _load(org, *, kind, listing_ids=(), requirement_id=None):
    if kind == TradeBlast.Kind.FLATS:
        ids = [str(x) for x in (listing_ids or [])]
        if not ids:
            raise TradeError("Pick at least one flat from your inventory")
        if len(ids) > MAX_FLATS:
            raise TradeError(f"At most {MAX_FLATS} flats in one blast")
        listings = list(
            Listing.objects.filter(org=org, pk__in=ids, archived_at__isnull=True, withdrawn_by_owner=False).select_related(
                "unit__building__society__locality"
            )
        )
        if len(listings) != len(set(ids)):
            raise TradeError("You can only share flats you currently handle")
        return listings, None, [flat_summary(li) for li in listings]
    if kind == TradeBlast.Kind.REQUIREMENT:
        req = Requirement.objects.filter(org=org, pk=requirement_id, active=True).first() if requirement_id else None
        if req is None:
            raise TradeError("Pick one of your customers' requirements")
        return [], req, [requirement_summary(req)]
    raise TradeError("Choose: flats or a requirement")


def preview(org, *, user, kind, listing_ids=(), requirement_id=None, scope="radius", radius_km=DEFAULT_RADIUS_KM, contact_ids=None):
    listings, req, items = _load(org, kind=kind, listing_ids=listing_ids, requirement_id=requirement_id)
    rows = audience(org, centre_points=centres(listings, req), scope=scope, radius_km=radius_km, contact_ids=contact_ids)
    return {
        "text": default_text(kind, org=org, user=user, items=items),
        "items": items,
        "reach": counts(rows),
        "radius_km": max(0.5, min(float(radius_km or DEFAULT_RADIUS_KM), MAX_RADIUS_KM)),
        "contacts": [contact_json(r["contact"], r["distance_km"]) | {"in_radius": r["in_radius"], "selected": r["selected"]} for r in rows],
    }


@transaction.atomic
def send(org, *, user, kind, text_="", listing_ids=(), requirement_id=None, scope="radius", radius_km=DEFAULT_RADIUS_KM, contact_ids=None):
    listings, req, items = _load(org, kind=kind, listing_ids=listing_ids, requirement_id=requirement_id)
    message = (text_ or "").strip() or default_text(kind, org=org, user=user, items=items)
    if len(message) > MAX_TEXT:
        raise TradeError(f"Keep it under {MAX_TEXT} characters")
    rows = [
        r
        for r in audience(org, centre_points=centres(listings, req), scope=scope, radius_km=radius_km, contact_ids=contact_ids)
        if r["selected"]
    ]
    if not rows:
        raise TradeError("Nobody selected. Widen the distance, choose everyone, or tick names.")
    blast = TradeBlast.objects.create(
        org=org,
        created_by=user,
        kind=kind,
        text=message,
        items=items,
        listing_ids=[str(li.pk) for li in listings],
        requirement=req,
        audience={"scope": scope, "radius_km": radius_km, "contact_ids": [str(r["contact"].pk) for r in rows]},
        recipients_total=len(rows),
    )
    firms = {}
    whatsapp = []
    for r in rows:
        c = r["contact"]
        if c.platform_org_id and c.platform_org_id != org.pk:
            firms.setdefault(c.platform_org_id, c)
        else:
            invite = f"{message}\n\n(Sent from Only Broker. Trade offers from brokers you know, in one place: {settings.OB_APP_URL})"
            whatsapp.append({"contact_id": str(c.pk), "name": c.name, "firm": c.firm, "whatsapp_url": whatsapp_link(c.phone, invite)})
    phone_enc = crypto.encrypt(user.phone)
    with rls.platform_context():
        for firm_id in firms:
            TradeDelivery.objects.create(
                org_id=firm_id,
                blast_id=blast.pk,
                from_org=org,
                from_name=org.name,
                from_phone_enc=phone_enc,
                kind=kind,
                text=message,
                items=items,
            )
            notify_org(firm_id, "trade_blast", {"blast_id": str(blast.pk), "from": org.name, "kind": kind}, realtime_event="trade.blast")
    blast.delivered_in_app = len(firms)
    blast.via_whatsapp = len(whatsapp)
    blast.save(update_fields=["delivered_in_app", "via_whatsapp"])
    return blast, whatsapp


# --- the receiving side -------------------------------------------------------------------------


def delivery_json(d: TradeDelivery) -> dict:
    return {
        "id": str(d.pk),
        "kind": d.kind,
        "from": d.from_name,
        "from_phone": d.from_phone,
        "text": d.text,
        "items": d.items,
        "reply": d.reply or None,
        "read": d.read_at is not None,
        "created_at": d.created_at.isoformat(),
    }


def inbox(org, limit=100):
    return list(TradeDelivery.objects.filter(org=org).order_by("-created_at")[:limit])


@transaction.atomic
def reply(delivery: TradeDelivery, *, org, user, answer: str, message: str = "") -> TradeDelivery:
    if answer not in (TradeDelivery.Reply.HAVE_CUSTOMER, TradeDelivery.Reply.HAVE_FLAT, TradeDelivery.Reply.NOT_NOW):
        raise TradeError("Answer: have a customer, have a flat, or not now")
    first = not delivery.reply
    delivery.reply = answer
    delivery.replied_at = timezone.now()
    delivery.read_at = delivery.read_at or delivery.replied_at
    delivery.save(update_fields=["reply", "replied_at", "read_at"])
    if answer != TradeDelivery.Reply.NOT_NOW and first:
        with rls.platform_context():
            TradeReply.objects.create(
                org_id=delivery.from_org_id,
                blast_id=delivery.blast_id,
                from_org=org,
                from_name=org.name,
                from_phone_enc=crypto.encrypt(user.phone),
                message=text(message, 300),
            )
            notify_org(
                delivery.from_org_id,
                "trade_reply",
                {"blast_id": str(delivery.blast_id), "from": org.name, "answer": answer},
                realtime_event="trade.reply",
            )
    return delivery


def mark_read(org) -> int:
    return TradeDelivery.objects.filter(org=org, read_at__isnull=True).update(read_at=timezone.now())


def blast_json(b: TradeBlast, with_replies=False) -> dict:
    out = {
        "id": str(b.pk),
        "kind": b.kind,
        "text": b.text,
        "items": b.items,
        "recipients_total": b.recipients_total,
        "delivered_in_app": b.delivered_in_app,
        "via_whatsapp": b.via_whatsapp,
        "replies_count": b.replies.count(),
        "audience": {k: v for k, v in b.audience.items() if k != "contact_ids"},
        "created_at": b.created_at.isoformat(),
    }
    if with_replies:
        out["replies"] = [
            {"from": r.from_name, "phone": r.from_phone, "message": r.message, "at": r.created_at.isoformat()}
            for r in b.replies.order_by("-created_at")
        ]
    return out
