"""Broadcasts: a broker's news to many of their own customers (D16).

The customer list is the broker's second asset (after inventory). A broadcast only ever reaches the
sending firm's own customers. Pilot rules from the founder: delivered in the app; sent to all of the
firm's customers (a customer can still turn off a broker's updates); free during the pilot, counted for
credits later. Customers not on the app yet are listed with a ready WhatsApp invite, so adding offline
customers to the platform pays off for the broker.
"""

from urllib.parse import quote

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.masterdata.models import Locality
from common import rls
from common.notify import notify_user

from .models import Broadcast, Customer

MAX_TEXT = 500


class BroadcastError(Exception):
    pass


def _inr(n) -> str:
    if n is None:
        return ""
    n = int(n)
    if n >= 10_000_000:
        return f"₹{n / 10_000_000:.2f} Cr".replace(".00", "")
    if n >= 100_000:
        return f"₹{n / 100_000:.1f} L".replace(".0 ", " ")
    s = str(n)
    head, tail = s[:-3], s[-3:]
    while len(head) > 2:
        tail = f"{head[-2:]},{tail}"
        head = head[:-2]
    return f"₹{head},{tail}" if head else f"₹{tail}"


def flat_summary(listing) -> dict:
    """What customers see about a flat in a broadcast: society-level only, never the flat number."""
    u = listing.unit
    soc = u.building.society
    bhk = "1 RK" if float(u.bhk) == 0.5 else f"{float(u.bhk):g} BHK"
    return {
        "society": soc.canonical_name,
        "locality": soc.locality.name,
        "bhk": bhk,
        "txn_type": listing.txn_type,
        "price": listing.price,
        "price_label": f"{_inr(listing.price)}{'/month' if listing.txn_type == 'RENT' else ''}" if listing.price else "",
        "available_from": listing.available_from.isoformat() if listing.available_from else None,
    }


def default_text(kind: str, *, org, listing=None, locality: Locality | None = None) -> str:
    if kind == Broadcast.Kind.NEW_FLAT and listing is not None:
        f = flat_summary(listing)
        what = "for rent" if f["txn_type"] == "RENT" else "for sale"
        price = f" — {f['price_label']}" if f["price_label"] else ""
        return f"New {f['bhk']} {what} in {f['society']}, {f['locality']}{price}. Reply to see it. — {org.name}"
    if kind == Broadcast.Kind.PRICE_DROP:
        where = locality.name if locality else "your preferred area"
        return f"Good news: rents have come down in {where}. Ask us for the latest flats. — {org.name}"
    return ""


def audience(org, *, scope: str = "all", locality: Locality | None = None):
    """This firm's customers only (RLS); 'locality' = those whose active requirement includes the area."""
    qs = Customer.objects.filter(org=org).exclude(stage=Customer.Stage.LOST)
    if scope == "locality" and locality is not None:
        qs = qs.filter(requirements__active=True, requirements__localities=locality).distinct()
    return qs


def counts(qs) -> dict:
    total = qs.count()
    on_app = qs.filter(platform_user__isnull=False)
    muted = on_app.filter(updates_muted=True).count()
    reach = on_app.count() - muted
    return {"total": total, "in_app": reach, "muted": muted, "not_on_app": total - reach - muted}


def invite_text(org, message: str) -> str:
    return f"{message}\n\nGet updates like this from {org.name} on the Only Broker app: {settings.OB_APP_URL}"


def whatsapp_link(phone_e164: str, text: str) -> str:
    return f"https://wa.me/{phone_e164.lstrip('+')}?text={quote(text)}"


@transaction.atomic
def send(org, *, user, kind: str, text: str, listing=None, locality=None, scope: str = "all") -> tuple[Broadcast, list[dict]]:
    text = (text or "").strip() or default_text(kind, org=org, listing=listing, locality=locality)
    if kind not in Broadcast.Kind.values:
        raise BroadcastError("Choose: new flat, price drop or news")
    if not text:
        raise BroadcastError("Write the message")
    if len(text) > MAX_TEXT:
        raise BroadcastError(f"Keep it under {MAX_TEXT} characters")
    if listing is not None and (listing.org_id != org.pk or listing.withdrawn_by_owner or listing.archived_at):
        raise BroadcastError("You can only announce flats you currently handle")
    qs = audience(org, scope=scope, locality=locality)
    c = counts(qs)
    b = Broadcast.objects.create(
        org=org,
        created_by=user,
        kind=kind,
        text=text,
        listing=listing,
        locality=locality,
        audience={"scope": scope, "locality_id": str(locality.pk) if locality else None},
        recipients_total=c["total"],
        delivered_in_app=c["in_app"],
        not_on_app=c["not_on_app"],
        muted=c["muted"],
    )
    payload = {
        "broadcast_id": str(b.pk),
        "org_id": str(org.pk),
        "org": org.name,
        "kind": kind,
        "text": text,
        "flat": flat_summary(listing) if listing is not None else None,
        "sent_at": timezone.now().isoformat(),
    }
    for cust in qs.filter(platform_user__isnull=False, updates_muted=False).select_related("platform_user"):
        notify_user(cust.platform_user, "broadcast", payload)
    offline = [
        {"customer_id": str(cust.pk), "name": cust.name or "Customer", "whatsapp_url": whatsapp_link(cust.phone, invite_text(org, text))}
        for cust in qs.filter(platform_user__isnull=True).order_by("name")[:300]
    ]
    return b, offline


# --- the customer's side --------------------------------------------------------------------------


def my_updates(user, limit: int = 100) -> list[dict]:
    from common.models import Notification

    items = Notification.objects.filter(user=user, template="broadcast").order_by("-created_at")[:limit]
    with rls.platform_context():
        muted = set(Customer.objects.filter(platform_user=user, updates_muted=True).values_list("org_id", flat=True))
    return [
        {**n.payload, "id": str(n.pk), "read": n.read_at is not None, "muted": n.payload.get("org_id") in {str(m) for m in muted}}
        for n in items
    ]


def set_muted(user, org_id, muted: bool) -> int:
    """A customer turns a broker's updates off (or back on). Only their own record with that broker changes."""
    with rls.platform_context():
        return Customer.objects.filter(platform_user=user, org_id=org_id).update(updates_muted=muted)


def mark_read(user) -> int:
    from common.models import Notification

    return Notification.objects.filter(user=user, template="broadcast", read_at__isnull=True).update(read_at=timezone.now())
